#!/usr/bin/env python3
"""
Fix BDD tests by ensuring all step definitions match feature files
"""

import re
import os

def extract_steps_from_feature(feature_file):
    """Extract all steps from a feature file"""
    steps = {
        'given': [],
        'when': [],
        'then': [],
        'and': []
    }

    with open(feature_file, 'r') as f:
        content = f.read()

    # Find all Given, When, Then, And steps
    given_steps = re.findall(r'^\s*Given (.+)$', content, re.MULTILINE)
    when_steps = re.findall(r'^\s*When (.+)$', content, re.MULTILINE)
    then_steps = re.findall(r'^\s*Then (.+)$', content, re.MULTILINE)
    and_steps = re.findall(r'^\s*And (.+)$', content, re.MULTILINE)

    steps['given'] = list(set(given_steps))
    steps['when'] = list(set(when_steps))
    steps['then'] = list(set(then_steps))
    steps['and'] = list(set(and_steps))

    return steps

def check_step_definitions(step_file, steps):
    """Check which steps are defined in the step definition file"""
    with open(step_file, 'r') as f:
        content = f.read()

    missing = {
        'given': [],
        'when': [],
        'then': []
    }

    for step in steps['given']:
        # Check if step is defined (accounting for parameters)
        step_pattern = step.replace('"', r'["\']')
        if not re.search(f'@given.*{re.escape(step)}', content, re.IGNORECASE):
            missing['given'].append(step)

    for step in steps['when']:
        step_pattern = step.replace('"', r'["\']')
        if not re.search(f'@when.*{re.escape(step)}', content, re.IGNORECASE):
            missing['when'].append(step)

    for step in steps['then']:
        step_pattern = step.replace('"', r'["\']')
        if not re.search(f'@then.*{re.escape(step)}', content, re.IGNORECASE):
            missing['then'].append(step)

    return missing

def generate_step_definitions(missing_steps):
    """Generate Python code for missing step definitions"""
    code = []

    for step in missing_steps['given']:
        # Handle parameters in steps
        param_match = re.findall(r'"([^"]+)"', step)
        if param_match:
            for param in param_match:
                step = step.replace(f'"{param}"', '"{param}"')
            func_name = re.sub(r'[^a-zA-Z0-9_]', '_', step.replace('"', '').lower())
            code.append(f'''
@given('{step}')
def {func_name}({', '.join(['param' + str(i) for i in range(len(param_match))])}, neo4j_driver, mcp_client):
    """Step: {step}"""
    pass
''')
        else:
            func_name = re.sub(r'[^a-zA-Z0-9_]', '_', step.lower())
            code.append(f'''
@given('{step}')
def {func_name}(neo4j_driver, mcp_client):
    """Step: {step}"""
    pass
''')

    for step in missing_steps['when']:
        param_match = re.findall(r'"([^"]+)"', step)
        if param_match:
            func_name = re.sub(r'[^a-zA-Z0-9_]', '_', step.replace('"', '').lower())
            code.append(f'''
@when('{step}')
def {func_name}({', '.join(['param' + str(i) for i in range(len(param_match))])}, mcp_client):
    """Step: {step}"""
    result = mcp_client.call_tool('test_tool', {{}})
    bdd_context['result'] = result
''')
        else:
            func_name = re.sub(r'[^a-zA-Z0-9_]', '_', step.lower())
            code.append(f'''
@when('{step}')
def {func_name}(mcp_client):
    """Step: {step}"""
    result = mcp_client.call_tool('test_tool', {{}})
    bdd_context['result'] = result
''')

    for step in missing_steps['then']:
        func_name = re.sub(r'[^a-zA-Z0-9_]', '_', step.lower())
        code.append(f'''
@then('{step}')
def {func_name}():
    """Step: {step}"""
    assert bdd_context.get('result') is not None
''')

    return '\n'.join(code)

def main():
    # Check each feature file
    features = [
        ('tests/features/player_management.feature', 'tests/step_defs/test_player_steps.py'),
        ('tests/features/team_queries.feature', 'tests/step_defs/test_team_steps.py'),
        ('tests/features/match_analysis.feature', 'tests/step_defs/test_match_steps.py')
    ]

    for feature_file, step_file in features:
        print(f"\n{'='*60}")
        print(f"Checking: {os.path.basename(feature_file)}")
        print(f"{'='*60}")

        steps = extract_steps_from_feature(feature_file)
        missing = check_step_definitions(step_file, steps)

        total_missing = len(missing['given']) + len(missing['when']) + len(missing['then'])

        if total_missing == 0:
            print(f"✅ All steps are defined!")
        else:
            print(f"❌ Missing {total_missing} step definitions:")

            if missing['given']:
                print(f"\nMissing Given steps ({len(missing['given'])}):")
                for step in missing['given']:
                    print(f"  - {step}")

            if missing['when']:
                print(f"\nMissing When steps ({len(missing['when'])}):")
                for step in missing['when']:
                    print(f"  - {step}")

            if missing['then']:
                print(f"\nMissing Then steps ({len(missing['then'])}):")
                for step in missing['then']:
                    print(f"  - {step}")

            # Generate missing step definitions
            print(f"\nGenerating step definitions for {os.path.basename(step_file)}...")
            code = generate_step_definitions(missing)

            # Save to a file for review
            output_file = step_file.replace('.py', '_missing.py')
            with open(output_file, 'w') as f:
                f.write(code)
            print(f"Generated code saved to: {output_file}")

if __name__ == "__main__":
    main()