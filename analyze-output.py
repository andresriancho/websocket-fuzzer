from __future__ import print_function

import glob
import argparse
import json
import numpy as np
import sklearn.cluster
import distance

from websocket_fuzzer.analysis.response_analyzer import analyze_response


IGNORE_MESSAGES = {'error',
                   'xml',
                   'sqlattempt1',
                   'sqlattempt2'}


def distance_len(s1, s2):
    return len(s1) - len(s2)


def extract_description_from_message(message):
    try:
        return json.loads(message)['description']
    except:
        return 'Invalid JSON message: %s' % message


def unique_responses(output_path):
    max_count = get_max_socket_message_count(output_path)
    listing = glob.glob(output_path + '*-%s.log' % max_count)

    messages = [file(filename).read() for filename in listing]
    messages = [extract_description_from_message(m) for m in messages]
    messages = set(list(messages))

    print('')
    print('Unique websocket responses:')
    print('')

    for description in messages:
        print(' - "%s"' % description)


def cluster_similar_responses(output_path):
    max_count = get_max_socket_message_count(output_path)
    listing = glob.glob(output_path + '*-%s.log' % max_count)

    messages = [file(filename).read() for filename in listing]
    messages = [extract_description_from_message(m) for m in messages]
    messages = np.asarray(messages)

    print()
    print('Clustering %s responses...(this might take a while)' % len(messages))
    print()

    lev_similarity = -1 * np.array([[distance.levenshtein(m1, m2) for m1 in messages] for m2 in messages])

    affprop = sklearn.cluster.AffinityPropagation(affinity='precomputed',
                                                  damping=0.5)
    affprop.fit(lev_similarity)

    print('Generated clusters:')
    print()

    for cluster_id in np.unique(affprop.labels_):
        exemplar = messages[affprop.cluster_centers_indices_[cluster_id]]
        cluster = np.unique(messages[np.nonzero(affprop.labels_ == cluster_id)])
        cluster_str = ', '.join(cluster)
        print('-' * 80)
        print(' - *%s:* %s' % (exemplar, cluster_str))
        print('-' * 80)
        print()


def analyze_responses_with_fingerprints(output_path):
    manual_analysis = []

    # This depends on how websocket_logfile.py saves the output
    for filename in glob.glob(output_path + '*.log'):
        if analyze_response(file(filename).read(), IGNORE_MESSAGES):
            manual_analysis.append(filename)

    if not manual_analysis:
        return

    print()
    print('These files require manual analysis:')
    print()

    for filename in manual_analysis:
        print(' - %s' % filename)


def get_max_socket_message_count(output_path):
    has_no_messages = 0
    max_has_no_messages = 10
    max_count = 0

    for count in xrange(100):

        # This depends on how websocket_logfile.py saves the output
        listing = glob.glob(output_path + '*-%s.log' % count)

        if not listing:
            has_no_messages += 1
            if has_no_messages >= max_has_no_messages:
                break

            continue

        max_count = count

    # -1 because the last message will always be /closed
    return max_count - 1


def analyze_websocket_message_count(output_path):
    print()
    print('Most common message count per connection:')
    print()

    counts = {}

    for count in reversed(xrange(100)):

        # This depends on how websocket_logfile.py saves the output
        listing = glob.glob(output_path + '*-%s.log' % count)

        connection_ids = []

        for filename in listing:
            filename = filename.replace(output_path, '')
            connection_id = filename.replace('-%s.log' % count, '')

            all_connection_ids = {x for v in counts.itervalues() for x in v}

            if connection_id not in all_connection_ids:
                connection_ids.append(connection_id)

        counts[count] = connection_ids

    for count in reversed(counts.keys()):
        listing = counts[count]

        if not listing:
            continue

        listing_str = ', '.join(listing)
        print('Found %s connections that sent %s messages: %s' % (len(listing), count, listing_str))
        print()


def analyze_output(output_path):
    analyze_responses_with_fingerprints(output_path)
    analyze_websocket_message_count(output_path)
    # cluster_similar_responses()
    unique_responses(output_path)


def main():
    parser = argparse.ArgumentParser(description='Analyze fuzzer output')

    parser.add_argument('-o', action='store', dest='output_path', required=True,
                        help='Path to the fuzzer output directory (eg. "output/0/")')

    results = parser.parse_args()
    analyze_output(results.output_path)


if __name__ == '__main__':
    main()
