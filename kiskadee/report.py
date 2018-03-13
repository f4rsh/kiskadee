"""Provide reporter capabilities to kiskadee analyzers.

Every analyzer on kiskadee has differents reports results.
This module came to compute and deal with this differences.
"""
import kiskadee
from abc import ABCMeta, abstractmethod


class Report:
    """Abstraction of a analyzer reporter."""

    __metaclass__ = ABCMeta

    def __init__(self, results):
        """Initialize Report class."""
        self.results = results

    @abstractmethod
    def _compute_reports(self, results): pass

    @staticmethod
    def logger_message(errors, analyzer):
        """Logger of reporter computer methods."""
        kiskadee.logger.debug(
                "WARNING: There are " +
                "{} registers on JSON ".format(errors) +
                "that was not able to convert to " +
                "'{}' reports.".format(analyzer)
            )
        return


class CppcheckReport(Report):
    """Concrete reporter implementation to cppcheck analyzer."""

    def _compute_reports(self, analyzer):
        """Compute every report type for cppcheck analyzer."""
        result_dict = {
                'warning': 0,
                'error': 0,
                'style': 0
        }
        count_error = 0
        for result in self.results:
            if 'severity' in list(result.keys()):
                result_dict[result['severity']] += 1
            else:
                count_error += 1

        if count_error > 0:
            self.logger_message(count_error, analyzer)

        return result_dict


class FlawfinderReport(Report):
    """Concrete reporter implementation to flawfinder analyzer."""

    def _compute_reports(self, analyzer):
        """Compute every report type for flawfinder analyzer."""
        result_dict = {
                'severity_1': 0,
                'severity_2': 0,
                'severity_3': 0,
                'severity_4': 0,
                'severity_5': 0
        }
        count_error = 0
        for result in self.results:
            if 'severity' in list(result.keys()):
                result_dict['severity_' + result['severity']] += 1
            else:
                count_error += 1

        if count_error > 0:
            self.logger_message(count_error, analyzer)

        return result_dict
