PERF_FORMAT_STRING = "\
\tAccuracy: {:>0.{display_precision}f}\tPrecision: {:>0.{display_precision}f}\t\
Recall: {:>0.{display_precision}f}\tF1: {:>0.{display_precision}f}\tF2: {:>0.{display_precision}f}"
RESULTS_FORMAT_STRING = "\tTotal predictions: {:4d}\tTrue positives: {:4d}\tFalse positives: {:4d}\tFalse negatives: {:4d}\tTrue negatives: {:4d}"


class ConfusionMatrix:
    def __init__(self):
        self.true_negatives = 0
        self.false_negatives = 0
        self.true_positives = 0
        self.false_positives = 0

    def count(self, predictions, truths):
        wrong_predictions = []
        index = 0
        for prediction, truth in zip(predictions, truths):
            if prediction == 0 and truth == 0:
                self.true_negatives += 1
            elif prediction == 0 and truth == 1:
                self.false_negatives += 1
                wrong_predictions.append(index)
            elif prediction == 1 and truth == 0:
                self.false_positives += 1
                wrong_predictions.append(index)
            else:
                self.true_positives += 1
            index += 1
        return wrong_predictions

    def show(self):
        try:
            total_predictions = self.true_negatives + self.false_negatives + self.false_positives + self.true_positives
            accuracy = 1.0 * (self.true_positives + self.true_negatives) / total_predictions
            precision = 1.0 * self.true_positives / (self.true_positives + self.false_positives)
            recall = 1.0 * self.true_positives / (self.true_positives + self.false_negatives)
            f1 = 2.0 * self.true_positives / (2 * self.true_positives + self.false_positives + self.false_negatives)
            f2 = (1 + 2.0 * 2.0) * precision * recall / (4 * precision + recall)
            print PERF_FORMAT_STRING.format(accuracy, precision, recall, f1, f2, display_precision=5)
            print RESULTS_FORMAT_STRING.format(total_predictions, self.true_positives, self.false_positives,
                                               self.false_negatives,
                                               self.true_negatives)
            print ""
        except Exception:
            print "Got an exception"
