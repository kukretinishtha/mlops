import os

import joblib
from azureml.core import Datastore, Dataset, Run
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

from my_custom_package.utils.const import TRAINING_DATASTORE, MODEL_NAME
from my_custom_package.utils.transform_data import remove_collinear_cols


__here__ = os.path.dirname(__file__)


def get_df_from_datastore_path(datastore, datastore_path):
    # In our example we only have single files,
    # but these may be daily data dumps
    datastore_path = [(datastore, datastore_path)]
    dataset = Dataset.Tabular.from_delimited_files(
        path=datastore_path
    )
    dataframe = dataset.to_pandas_dataframe()
    return dataframe


def prepare_data(workspace):
    datastore = Datastore.get(workspace, TRAINING_DATASTORE)
    x_train = get_df_from_datastore_path(datastore, 'train/X_train.csv')
    y_train = get_df_from_datastore_path(datastore, 'train/y_train.csv')
    y_train = y_train['Target']
    x_test = get_df_from_datastore_path(datastore, 'test/X_test.csv')
    y_test = get_df_from_datastore_path(datastore, 'test/y_test.csv')
    y_test = y_test['Target']
    x_train = remove_collinear_cols(x_train)
    x_test = remove_collinear_cols(x_test)
    return x_train, y_train, x_test, y_test


def train_model(x_train, y_train):
    classifier = LogisticRegression()
    classifier.fit(x_train, y_train)
    return classifier


def evaluate_model(classifier, x_test, y_test, run):
    y_pred = classifier.predict(x_test)
    model_f1_score = f1_score(y_test, y_pred)
    run.log('F1_Score', model_f1_score)


def save_model(classifer):
    output_dir = os.path.join(__here__, 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, 'model.pkl')
    joblib.dump(classifer, model_path)
    return model_path


def register_model(run, model_path):
    run.upload_file(model_path, "outputs/model.pkl")
    model = run.register_model(
        model_name=MODEL_NAME,
        model_path="outputs/model.pkl"
    )
    run.log('Model_ID', model.id)


def main():
    run = Run.get_context()
    workspace = run.experiment.workspace
    x_train, y_train, x_test, y_test = prepare_data(workspace)
    classifier = train_model(x_train, y_train)
    evaluate_model(classifier, x_test, y_test, run)
    model_path = save_model(classifier)
    register_model(run, model_path)


if __name__ == '__main__':
    main()
