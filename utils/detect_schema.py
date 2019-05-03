from .utils import flatten_dict, parse_attribute, date_normalize
from .model import DecisionTreeModel, NaiveBayesModel, LogisticRegressionModel
from .preprocess import FeaturesTransformer
import json
import pickle
import re
import numpy as np


class JobSchemaDetection:
    def __init__(self, jobs, model_dir, standard_attributes_fn, weight_model_fn):
        self.excluded_attributes = ['baseSalary_minValue', 'baseSalary_maxValue', 'datePosted', 'validThrough']
        self.jobs = [flatten_dict(job) for job in jobs]
        self.__load_standard_attributes(standard_attributes_fn)
        self.__load_models(model_dir)
        self.__load_models_weight(weight_model_fn)
        self.__mapping_schema_many(self.jobs)

    def __load_standard_attributes(self, standard_attributes_fn):
        with open(standard_attributes_fn, mode='r', encoding='utf8') as f:
            self.standard_attributes = parse_attribute(json.load(f))
            f.close()

    def __load_models(self, model_dir):
        self.models = {}
        for attribute in self.standard_attributes:
            if attribute in self.excluded_attributes:
                continue
            self.models[attribute] = {}
            with open(f'{model_dir}/{attribute}/{attribute}_nb.pickle', mode='rb') as f:
                self.models[attribute]['nb'] = pickle.load(f)
                f.close()

            with open(f'{model_dir}/{attribute}/{attribute}_logistic.pickle', mode='rb') as f:
                self.models[attribute]['dtree'] = pickle.load(f)
                f.close()

    def __load_models_weight(self, weight_model_fn):
        with open(weight_model_fn, mode='r', encoding='utf8') as f:
            self.weight_model = json.load(f)
            f.close()

    def __calculate_proba(self, attribute_value, standard_attribute_name):
        attribute_value = str(attribute_value)
        proba = self.models[standard_attribute_name]['nb'].clf.predict_proba([attribute_value])[0][1] * \
                self.weight_model[standard_attribute_name][0] + \
                self.models[standard_attribute_name]['dtree'].clf.predict_proba([attribute_value])[0][1] * \
                self.weight_model[standard_attribute_name][1]
        return proba

    def get_mapping_schema(self):
        return self.schema_mapping

    def __mapping_schema_many(self, jobs):
        schemas = []
        for job in jobs:
            schemas.append(self.__mapping_schema_one(job))

        mapping_attributes = []
        for schema in schemas:
            mapping_attributes += schema.keys()

        mapping_attributes = list(set(mapping_attributes))

        sum_matrix = np.sum(
            (self.__create_matrix_by_matched_schema(schema, self.standard_attributes, mapping_attributes) for schema in
             schemas))

        matched_tuples = self.__match_by_matrix(sum_matrix)

        self.schema_mapping = {
            mapping_attributes[int(matched_tuple[0])]: self.standard_attributes[int(matched_tuple[1])] for
            matched_tuple in matched_tuples}

    @staticmethod
    def __create_matrix_by_matched_schema(schema, standard_attributes, mapping_attributes):
        matrix = np.zeros((len(mapping_attributes), len(standard_attributes)))
        for mapping_attribute, standard_attribute in schema.items():
            matrix[mapping_attributes.index(mapping_attribute)][standard_attributes.index(standard_attribute)] = 1

        return matrix

    def __mapping_schema_one(self, job):
        match_min_max_salary = self.__match_min_max_base_salary(job)
        mapping_schema = {**self.__match_attributes_date_type(job), **match_min_max_salary}

        remaining_standard_attributes = [attribute for attribute in self.standard_attributes if
                                         attribute not in mapping_schema.values() and attribute not in self.excluded_attributes]
        remaining_mapping_attributes = [attribute for attribute in job.keys() if
                                        attribute not in mapping_schema.keys() and attribute not in self.excluded_attributes]

        if len(match_min_max_salary) > 0:
            remaining_standard_attributes.remove("baseSalary_value")

        return {**mapping_schema,
                **self.__decide_attribute_match(job, remaining_standard_attributes, remaining_mapping_attributes)}

    def __decide_attribute_match(self, job, remaining_standard_attributes, remaining_mapping_attributes):
        decide_mapping = {}
        sim_matrix = []
        for key in remaining_mapping_attributes:
            sim_matrix.append(
                [self.__calculate_proba(job[key], attribute) for attribute in remaining_standard_attributes])
        mapping_tuples = self.__match_by_matrix(np.array(sim_matrix))
        for item in mapping_tuples:
            decide_mapping[remaining_mapping_attributes[int(item[0])]] = remaining_standard_attributes[int(item[1])]

        return decide_mapping

    @staticmethod
    def __match_by_matrix(matrix):
        min_dim = min(matrix.shape)

        matched = np.empty((0, 2))
        i = 0
        while i < min_dim:
            i += 1
            max_position = np.column_stack(np.where((matrix == matrix.max()) & (matrix > 0.5)))
            if max_position.shape[0] == 0:
                break
            else:
                max_position = max_position[0]
            matrix[:, max_position[1]] = -1
            matrix[max_position[0], :] = -1
            matched = np.concatenate((matched, max_position.reshape(1, 2)), axis=0)

        return matched

    def __match_attributes_date_type(self, job):
        date_attributes = {}
        for attribute, value in job.items():
            if self.__is_date(value):
                date_attributes[attribute] = value

        date_mapping = {}
        if len(date_attributes) == 2:
            items = list(date_attributes.items())
            if date_normalize(items[0][1]) < date_normalize(items[1][1]):
                date_mapping[items[0][0]] = 'datePosted'
                date_mapping[items[1][0]] = 'validThrough'
            else:
                date_mapping[items[1][0]] = 'datePosted'
                date_mapping[items[0][0]] = 'validThrough'
        return date_mapping

    def __match_min_max_base_salary(self, job):
        min_max_attributes = {}
        for attribute, value in job.items():
            if self.__is_salary(value):
                min_max_attributes[attribute] = value

        min_max_base_salary_mapping = {}
        if len(min_max_attributes) == 2:
            items = list(min_max_attributes.items())
            v0 = int(re.search(r'\d+', str(items[0][1])).group(0))
            v1 = int(re.search(r'\d+', str(items[1][1])).group(0))
            if v0 < v1:
                min_max_base_salary_mapping[items[0][0]] = 'baseSalary_minValue'
                min_max_base_salary_mapping[items[1][0]] = 'baseSalary_maxValue'
            else:
                min_max_base_salary_mapping[items[1][0]] = 'baseSalary_minValue'
                min_max_base_salary_mapping[items[0][0]] = 'baseSalary_maxValue'
        return min_max_base_salary_mapping

    @staticmethod
    def __is_date(attribute_value):
        return re.match(
            r"^(\d{4}-\d{2}-\d{2} {0,1}((\d{2}:\d{2}:\d{2})|T\d{2}:\d{2}(:\d{2})?(\+\d{2}:\d{2}))?)|(\d{2}\/\d{2}\/\d{4})|(\d{4}\/\d{2}\/\d{2})$",
            str(attribute_value)) is not None

    def __is_salary(self, attribute_value):
        return (self.__is_number(attribute_value) and not self.__is_postal_code(attribute_value)) or re.match(
            r'^\s*(\w+\s*)?\d+\s*(triệu|tr|trieu)$', str(attribute_value)) is not None

    @staticmethod
    def __is_number(attribute_value):
        return re.match(r"^(((\d{1,3}([\.,]\d{3})*)|(\d+))|(\w*\d+))$", str(attribute_value)) is not None

    @staticmethod
    def __is_postal_code(attribute_value):
        postal_codes = [880000, 790000, 960000, 260000, 230000, 220000, 930000, 820000, 590000, 830000, 800000, 970000,
                        270000, 900000, 550000, 630000, 640000, 380000, 810000, 870000, 600000, 310000, 400000, 480000,
                        170000, 180000, 910000, 350000, 160000, 650000, 920000, 580000, 390000, 240000, 330000, 670000,
                        850000, 420000, 430000, 660000, 290000, 620000, 510000, 560000, 570000, 200000, 520000, 950000,
                        360000, 840000, 410000, 250000, 530000, 860000, 940000, 300000, 890000, 280000, 320000]
        range_codes = [(100000, 150000), (700000, 760000), (460000, 470000), (440000, 450000)]

        int_value = int(attribute_value)

        if int_value in postal_codes:
            return True
        else:
            for range_code in range_codes:
                if int_value in range(range_code[0], range_code[1] + 1):
                    return True

            return False
