from operator import itemgetter

from sklearn.cluster import KMeans

from dev.common import extract_features_from_many_files

SAMPLE_RATE = 44100


def prune_training_population(training_files, desired_count):
    features_for_all_files = extract_features_from_many_files(training_files)
    predictions, distances = analyze_for_clusters(features_for_all_files, desired_count)
    indexed_predictions = list_to_indexed_map(predictions)
    representative_sample_indices = \
        [indices
         [min(enumerate([distances[index, cluster] for index in indices]), key=itemgetter(1))[0]]
         for cluster, indices in indexed_predictions.items()]
    return [features_for_all_files[index][0] for index in representative_sample_indices]


def analyze_for_clusters(features_for_all_files, count):
    k_means_obj = KMeans(count)
    predictions = k_means_obj.fit_predict(features_for_all_files)
    distances = k_means_obj.transform(features_for_all_files)
    return predictions, distances


def list_to_indexed_map(lst):
    result = {}
    for i, val in enumerate(lst):
        if not result.has_key(val):
            result[val] = []
        result[val].append(i)
    return result
