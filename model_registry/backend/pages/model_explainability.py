from dash import dcc, html

from model_registry.backend.components.top_toolbar import top_toolbar

#from sklearn.datasets import load_breast_cancer
#from sklearn.ensemble import RandomForestClassifier

#from shapash.explainer.smart_explainer import SmartExplainer


def model_explainability_layout():

   # data = load_breast_cancer(as_frame=True)
    #X = data.data
    #y = data.target

  #  model = RandomForestClassifier(n_estimators=50, random_state=42)
  #  model.fit(X, y)

   # xpl = SmartExplainer(model=model)
    #xpl.compile(x=X)

    # Shapash returns a Plotly Figure
    #fig = xpl.plot.features_importance()

    return html.Div(
        [
            top_toolbar(),
            html.H3("Model Explainability"),
            dcc.Graph(
                figure={},
                config={"displayModeBar": False}
            )
        ],
        style={"padding": "20px"}
    )
