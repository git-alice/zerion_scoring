import pandas as pd
from catboost import CatBoostClassifier, Pool


def set_model():
    model_params = dict(
            thread_count=8,
            iterations=2000,
            loss_function='CrossEntropy',
            eval_metric='CrossEntropy',
            allow_writing_files=False,
            save_snapshot=False
                        )
    model = CatBoostClassifier()
    model.set_params(**model_params)
    return model


def predict(test_df, model_path):
    test_pool = Pool(data=test_df)
    model = set_model()
    model.load_model(model_path, format='cbm')
    prediction = model.predict(test_pool, prediction_type='Probability')
    prediction = pd.DataFrame(prediction, index=test_df.index)
    return prediction