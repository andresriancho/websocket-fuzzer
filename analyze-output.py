from __future__ import print_function

import glob
import numpy as np
import sklearn.cluster
import distance

from websocket_fuzzer.analysis.response_analyzer import analyze_response


OUTPUT_PATH = 'output/'
IGNORE_MESSAGES = {'error',
                   'xml'}


def cluster_similar_responses():
    max_count = get_max_socket_message_count()
    listing = glob.glob(OUTPUT_PATH + '*-%s.log' % max_count)

    messages = [file(filename).read() for filename in listing]
    messages = np.asarray(messages)

    print()
    print('Clustering responses...(this might take a while)')
    print()

    lev_similarity = -1 * np.array([[distance.levenshtein(m1, m2) for m1 in messages] for m2 in messages])

    affprop = sklearn.cluster.AffinityPropagation(affinity='precomputed', damping=0.5)
    affprop.fit(lev_similarity)

    print('Generated clusters:')
    print()

    for cluster_id in np.unique(affprop.labels_):
        exemplar = messages[affprop.cluster_centers_indices_[cluster_id]]
        cluster = np.unique(messages[np.nonzero(affprop.labels_ == cluster_id)])
        cluster_str = ', '.join(cluster)
        print(' - *%s:* %s' % (exemplar, cluster_str))
        print()


def analyze_responses_with_fingerprints():
    manual_analysis = []

    # This depends on how websocket_logfile.py saves the output
    for filename in glob.glob(OUTPUT_PATH + '*.log'):
        if analyze_response(file(filename).read(), IGNORE_MESSAGES):
            manual_analysis.append(filename)

    if not manual_analysis:
        return

    print()
    print('These files require manual analysis:')
    print()

    for filename in manual_analysis:
        print(' - %s' % filename)


def get_max_socket_message_count():
    has_no_messages = 0
    max_has_no_messages = 10
    max_count = 0

    for count in xrange(100):

        # This depends on how websocket_logfile.py saves the output
        listing = glob.glob(OUTPUT_PATH + '*-%s.log' % count)

        if not listing:
            has_no_messages += 1
            if has_no_messages >= max_has_no_messages:
                break

            continue

        max_count = count

    # -1 because the last message will always be /closed
    return max_count - 1


def analyze_websocket_message_count():
    print()
    print('Most common message count per connection:')
    print()

    has_no_messages = 0
    max_has_no_messages = 10
    counts = {}

    for count in xrange(100):

        # This depends on how websocket_logfile.py saves the output
        listing = glob.glob(OUTPUT_PATH + '*-%s.log' % count)

        # break after many empty results
        if not listing:
            has_no_messages += 1
            if has_no_messages >= max_has_no_messages:
                break

            continue

        connection_ids = []

        for filename in listing:
            filename = filename.replace(OUTPUT_PATH, '')
            connection_id = filename.replace('-%s.log' % count, '')

            connection_ids.append(connection_id)

        counts[count] = connection_ids

    # Now cleanup the connection ids to show only the greatest count
    for count in reversed(counts.keys()):
        connection_ids = counts[count]

        if count - 1 not in counts:
            continue

        connection_ids_minus_one = counts[count -1]

        for connection_id in connection_ids:
            connection_ids_minus_one.remove(connection_id)

    for count in reversed(counts.keys()):
        listing = counts[count]
        listing_str = ', '.join(listing)
        print('Found %s connections that sent %s messages: %s' % (len(listing), count, listing_str))
        print()


def analyze_output():
    analyze_responses_with_fingerprints()
    analyze_websocket_message_count()
    cluster_similar_responses()


if __name__ == '__main__':
    analyze_output()
