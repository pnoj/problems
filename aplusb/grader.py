import argparse
import subprocess
from runner import run
import os
import yaml
import json

def get_single_testcase(testcase_dir, submission_file_path, timeout=None):
    testcase_name = os.path.basename(testcase_dir)
    input_file_path = os.path.join(testcase_dir, testcase_name + ".in")
    testcase_input_file = open(input_file_path, "r")
    testcase_input = testcase_input_file.read()
    testcase_input_file.close()

    output_file_path = os.path.join(testcase_dir, testcase_name + ".out")
    testcase_output_file = open(output_file_path, "r")
    testcase_output = testcase_output_file.read()
    testcase_output_file.close()

    result = run(testcase_input, submission_file_path, timeout)

    if result['status'] == 'EC':
        if result['data'] == testcase_output:
            result['status'] = 'AC'
        else:
            result['status'] = 'WA'

    result['name'] = testcase_name
    result['type'] = 'testcase'

    return result

def get_single_batch(batch_dir, submission_file_path, timeout):
    batch_name = os.path.basename(batch_dir)
    testcases = os.listdir(batch_dir)
    testcases.remove('manifest.yaml')
    result = {'testcases': [], 'score': {'scored': 0, 'scoreable': 0}}

    batch_config_file_path = os.path.join(batch_dir, "manifest.yaml")
    batch_config_file = open(batch_config_file_path, "r")
    batch_config_yaml = batch_config_file.read()
    batch_config_file.close()
    batch_config = yaml.safe_load(batch_config_yaml)
    result['score']['scoreable'] = batch_config['metadata']['points']
    points_per_testcase = result['score']['scoreable'] / len(testcases)

    for i in testcases:
        testcase_dir = os.path.join(bath_dir, i)
        testcase_result = get_single_testcase(testcase_dir, submission_file_path, timeout)
        result['testcases'].append(testcase_result)
        result['score']['scored'] += points_per_testcase
    result['name'] = batch_name
    result['type'] = 'batch'
    return result


def test(testcases_dir, submission_file_path, timeout):
    batches = os.listdir(testcases_dir)
    result = {'batches': []}
    for i in batches:
        batch_dir = os.path.join(testcases_dir, i)
        batch_result = get_single_batch(batch_dir, submission_file_path, timeout)
        result['batches'].append(batch_result)

    result['type'] = 'result'
    result['score'] = {'scored': 0, 'scoreable': 0}

    all_statuses = []
    for batch in result['batches']:
        for testcase in batch:
            all_statuses.append(testcase['status'])
        result['score']['scored'] += batch['score']['scored']
        result['score']['scoreable'] += batch['score']['scoreable']

    all_present_statuses = set(all_statuses)
    
    final_verdict = None
    if all_present_statuses == {'AC'}:
        final_verdict = 'AC'
    else:
        statuses = ['CE', 'IR', 'TLE', 'MLE', 'OLE', 'WA']
        for i in statuses:
            if i in all_present_statuses:
                final_verdict = i
                break

    if final_verdict == None:
        final_verdict = 'IE'

    return result

def main(args):
    testcases_dir = args['testcases_dir']
    submission_file_path = args['submission_file']
    timeout = args['timeout']

    result = test(testcases_dir, submission_file_path, timeout)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = vars(parser.parse_args())
    result = main(args)
    result_json = json.dumps(result)
    print(result_json)
