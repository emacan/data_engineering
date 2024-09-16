import recordlinkage
import pandas as pd
import commons.utils as utils
import numpy as np

main_directory = utils.get_absolute_path("../")
data = pd.read_csv(main_directory + '/mediated_schema.csv')

average_precision = 0
average_recall = 0
average_fscore = 0
n=5

# ---- BLOCKING ----
indexer = recordlinkage.Index()
indexer.block('name')
golden_links = indexer.index(data)
print(len(golden_links))



# ---- PAIRWISE MATCHING ----
compare_cl = recordlinkage.Compare()
compare_cl.string('name', 'name', method='jarowinkler', threshold=0.85, label='name')
compare_cl.string('category', 'category', method='jarowinkler', threshold=0.85, label='category')
compare_cl.string('country', 'country', method='jarowinkler', threshold=0.85, label='country')

golden_comparisons = compare_cl.compute(golden_links, data)
scores = np.average(
    golden_comparisons.values,
    axis=1,
    weights=[50,30,20])
scored_golden_comparisons = golden_comparisons.assign(scores=scores)
matches = scored_golden_comparisons[scored_golden_comparisons['scores'] >= 0.7]


for i in range (1,n):
    random_indexer = recordlinkage.Index()
    random_indexer.random(10000000)
    random_links = random_indexer.index(data)
    random_comparisons = compare_cl.compute(random_links, data)
    random_scores = np.average(
        random_comparisons.values,
        axis=1,
        weights=[50,30,20])
    scored_random_comparisons = random_comparisons.assign(scores=random_scores)
    random_matches = scored_random_comparisons[scored_random_comparisons['scores'] >= 0.7]

    precision = recordlinkage.precision(matches, random_matches)
    recall = recordlinkage.recall(matches, random_matches)
    fscore = recordlinkage.fscore(matches, random_matches)
    print("Experiment n." + str(i) + ":")
    print("precision: " + str(precision))
    print("recall: " + str(recall))
    print("fscore: " + str(fscore))
    print("\n")
    average_precision += precision
    average_recall += recall
    average_fscore += fscore

average_precision = average_precision / n
average_recall = average_recall / n
average_fscore = average_fscore / n

print("average_precision: " + str(average_precision))
print("average_recall: " + str(average_recall))
print("average_fscore: " + str(average_fscore))

