#!/usr/bin/env python3
"""
Demand Curve Course Extractor
Uses browser-use CLI to extract course content
"""
import subprocess
import json
import re
import time
import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

def run_browser(cmd, session="dc"):
    """Run a browser-use command and return result"""
    full_cmd = f'uv tool run browser-use --session {session} {cmd}'
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()

def js_eval(code, session="dc"):
    """Execute JavaScript and return result"""
    # Escape the code for shell
    escaped = code.replace('"', '\\"').replace('\n', ' ')
    result = run_browser(f'eval "{escaped}"', session)
    # Parse the result
    if result.startswith('result: '):
        return result[8:]
    return result

def extract_course(course_url, session="dc"):
    """Extract all content from a course"""
    course_slug = course_url.split('/courses/')[-1]
    print(f"\n{'='*60}")
    print(f"Extracting course: {course_slug}")
    print(f"{'='*60}")

    # Navigate to course page
    run_browser(f'open "{course_url}"', session)
    time.sleep(2)

    # Get course metadata
    metadata = js_eval('''
        const title = document.querySelector('h1')?.innerText || '';
        const about = document.body.innerText.match(/About this course[\\s\\S]*?(?=Syllabus)/)?.[0] || '';
        const syllabus = document.body.innerText.match(/Syllabus[\\s\\S]*?(?=Next|Continue|Start)/)?.[0] || '';
        JSON.stringify({title, about, syllabus});
    ''', session)

    try:
        course_data = json.loads(metadata)
    except:
        course_data = {'title': course_slug, 'about': '', 'syllabus': ''}

    # Find first lesson link
    first_lesson = js_eval('''
        const link = document.querySelector('a[href*="/lessons/"]');
        link ? link.href : '';
    ''', session)

    if not first_lesson:
        # Try "Continue Course" or "Start Course" button
        first_lesson = js_eval('''
            const link = Array.from(document.querySelectorAll('a')).find(a =>
                a.innerText.includes('Continue') || a.innerText.includes('Start Course')
            );
            link ? link.href : '';
        ''', session)

    lessons = []
    visited = set()
    current_url = first_lesson

    # Navigate through all lessons
    while current_url and current_url not in visited:
        visited.add(current_url)
        print(f"  Extracting: {current_url.split('/')[-1]}")

        run_browser(f'open "{current_url}"', session)
        time.sleep(1.5)

        # Scroll to load content
        for _ in range(3):
            run_browser('scroll down', session)
            time.sleep(0.3)

        # Extract lesson content
        content = js_eval('''
            const body = document.body.innerText;
            const start = body.indexOf('LESSON');
            const end = body.indexOf('💬\\nNext');
            if (start > -1 && end > start) {
                body.substring(start, end);
            } else {
                body.substring(0, 8000);
            }
        ''', session)

        lesson_title = js_eval("document.querySelector('h1, h2')?.innerText || ''", session)

        lessons.append({
            'url': current_url,
            'title': lesson_title,
            'content': content
        })

        # Find next lesson
        next_url = js_eval('''
            const next = Array.from(document.querySelectorAll('a')).find(a =>
                a.innerText.trim() === 'Next' && a.href.includes('/lessons/')
            );
            next ? next.href : '';
        ''', session)

        if next_url and 'Feedback' in next_url:
            print("  Reached feedback - course complete")
            break

        current_url = next_url if next_url else None

    # Write MD file
    md_content = f"""# {course_data.get('title', course_slug)}

**URL:** {course_url}
**Extracted:** {time.strftime('%Y-%m-%d')}

---

## About This Course

{course_data.get('about', 'N/A')}

---

## Syllabus

{course_data.get('syllabus', 'N/A')}

---

## Lessons

"""

    for i, lesson in enumerate(lessons, 1):
        md_content += f"""
### Lesson {i}: {lesson.get('title', 'Unknown')}

**URL:** {lesson.get('url', '')}

{lesson.get('content', '')}

---
"""

    # Save file
    output_file = OUTPUT_DIR / f"{course_slug}.md"
    output_file.write_text(md_content)
    print(f"  Saved: {output_file}")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_course.py <course_url>")
        sys.exit(1)

    extract_course(sys.argv[1])
