1. Goals
Problem : 
  You aim to develop a robust Rust program or library.
Output/Insight Needed : 
  Idiomatic Rust code accompanied by thorough unit tests.
Type of Response : 
  Code snippet with comments explaining the logic, followed by unit tests.

Goal Statement :
  "Write idiomatic Rust code for a function that performs {{ user_task }}, ensuring it handles all expected inputs correctly. Follow this by writing unit tests covering base cases, common scenarios, and edge cases."

2. Return Format
Code Presentation :
  Begin with a short description of the function or module.
  Provide the Rust code in a clear, idiomatic style.
  Use comments to explain complex parts or logic decisions.
Unit Tests :
  Write unit tests in a #[cfg(test)] mod block.
  Include separate test functions for base cases, common cases, and edge cases.
  Clearly label each section of the tests using comments.
Stylistic Guidelines :
  Use snake_case for function names and variable identifiers.
  Avoid unnecessary use of unwrap(); handle errors gracefully with Result or Option.
  Ensure code is formatted according to Rust's style guide (use rustfmt).

Format Statement :
  "Return the idiomatic Rust function in a single block. Follow this by unit tests formatted as bullet points or numbered lists within a test module."

3. Warnings
Caveats :
  Avoid overly complex logic without explanation.
Constraints :
  Adhere to Rust's safety and concurrency principles.
  Consider performance implications in your code design.

Warning Statement :
  "Ensure code follows best practices for safety, avoiding unsafe blocks unless absolutely necessary. Handle errors gracefully."

4. Context Dump
# {{ project_name }} Codebase & Dependencies

## File List
{% for file in files %}
- {{ file.path }} ({{ file.language }}, {{ file.size }} bytes)
{% endfor %}

## File Contents

{% for file in files %}
### {{ file.path }}

{{ file.language }}
{{ file.content }}


{% endfor %}
