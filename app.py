from dash import Dash, html, dcc, callback, Output, Input, no_update
import plotly.express as px
import pandas as pd

url = "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"

try:
    df = pd.read_csv(url)
except Exception:
    # Резервный вариант: встроенный датасет Plotly.
    # Он позволяет запустить приложение даже при временной недоступности GitHub.
    df = px.data.gapminder()

df = df.dropna(subset=["country", "continent", "year", "lifeExp", "pop", "gdpPercap"]).copy()
df["year"]=df["year"].astype(int)

years=sorted(df["year"].unique().tolist())
countries=sorted(df["country"].unique().tolist())

labels = {
    "pop": "Население",
    "lifeExp": "Ожидаемая продолжительность жизни",
    "gdpPercap": "ВВП на душу населения",
}
measure_options = [
    {"label": label, "value": value}
    for value, label in labels.items()
]

default_countries = [
    c for c in ["Canada", "United States", "China", "India", "Germany"]
    if c in countries
]
default_year = 2007 if 2007 in years else max(years)

app=Dash(__name__)
server=app.server
app.title="Демография — Gapminder Dashboard"

page_style = {
    "fontFamily": "Inter, Arial, sans-serif",
    "background": "#F5F7FB",
    "minHeight": "100vh",
    "padding": "24px",
    "color": "#172033",
}
header_style = {
    "maxWidth": "1500px",
    "margin": "0 auto 18px auto",
}
filter_style = {
    "maxWidth": "1500px",
    "margin": "0 auto 18px auto",
    "background": "white",
    "padding": "18px",
    "borderRadius": "16px",
    "boxShadow": "0 6px 24px rgba(24, 39, 75, 0.06)",
}
controls_style = {
    "display": "grid",
    "gridTemplateColumns": "repeat(5, minmax(180px, 1fr))",
    "gap": "14px",
}
graphs_style = {
    "maxWidth": "1500px",
    "margin": "0 auto",
    "display": "grid",
    "gridTemplateColumns": "repeat(2, minmax(0, 1fr))",
    "gap": "18px",
}
card_style = {
    "background": "white",
    "borderRadius": "16px",
    "boxShadow": "0 6px 24px rgba(24, 39, 75, 0.06)",
    "padding": "10px 12px 2px 12px",
    "minHeight": "430px",
}
label_style = {
    "fontSize": "12px",
    "fontWeight": "700",
    "color": "#64748B",
    "marginBottom": "6px",
    "display": "block",
    "textTransform": "uppercase",
    "letterSpacing": "0.04em",
}

def control(label, component):
    return html.Div([
        html.Label(label, style=label_style),
        component
    ])

app.layout = html.Div([
    html.Div([
        html.H1(
            "Демографический дашборд Gapminder",
            style={"margin": "0", "fontSize": "30px", "fontWeight": "800"}
        ),
    ], style=header_style),

    html.Div([
        html.Div([
            control(
                "Страны",
                dcc.Dropdown(
                    options=[{"label": c, "value": c} for c in countries],
                    value=default_countries,
                    multi=True,
                    id="country-selection",
                    placeholder="Выберите страны..."
                )
            ),
            control(
                "Y линейного графика",
                dcc.Dropdown(
                    options=measure_options,
                    value="pop",
                    clearable=False,
                    id="line-y"
                )
            ),
            control(
                "X пузырьковой диаграммы",
                dcc.Dropdown(
                    options=measure_options,
                    value="gdpPercap",
                    clearable=False,
                    id="bubble-x"
                )
            ),
            control(
                "Y пузырьковой диаграммы",
                dcc.Dropdown(
                    options=measure_options,
                    value="lifeExp",
                    clearable=False,
                    id="bubble-y"
                )
            ),
            control(
                "Размер пузырька",
                dcc.Dropdown(
                    options=measure_options,
                    value="pop",
                    clearable=False,
                    id="bubble-size"
                )
            ),
        ], style=controls_style),

        html.Div([
            html.Label("Год — общий кросс-фильтр", style=label_style),
            dcc.Slider(
                min=min(years),
                max=max(years),
                step=None,
                marks={int(y): str(y) for y in years if y % 5 == 0 or y in (min(years), max(years))},
                value=default_year,
                id="year-filter",
                tooltip={"always_visible": True, "placement": "bottom"}
            ),
        ], style={"marginTop": "22px"})
    ], style=filter_style),

    html.Div([
        html.Div([
            dcc.Graph(id="line-chart", config={"displaylogo": False})
        ], style=card_style),

        html.Div([
            dcc.Graph(id="bubble-chart", config={"displaylogo": False})
        ], style=card_style),

        html.Div([
            dcc.Graph(id="top15-chart", config={"displaylogo": False})
        ], style=card_style),

        html.Div([
            dcc.Graph(id="continent-pie", config={"displaylogo": False})
        ], style=card_style),
    ], style=graphs_style),

    html.Div(
        "Источник: Plotly Gapminder dataset. Линейный график управляет годом через clickData.",
        style={
            "maxWidth": "1500px",
            "margin": "16px auto 0 auto",
            "fontSize": "12px",
            "color": "#94A3B8",
            "textAlign": "right"
        }
    )
], style=page_style)


@callback(
    Output("line-chart", "figure"),
    Input("country-selection", "value"),
    Input("line-y", "value"),
    Input("year-filter", "value"),
)
def update_line(countries, y_measure, selected_year):
    countries = countries or []
    dff = df[df["country"].isin(countries)].copy()

    if dff.empty:
        fig = px.scatter(title="Выберите хотя бы одну страну")
        fig.update_layout(template="plotly_white")
        return fig

    fig = px.line(
        dff.sort_values(["country", "year"]),
        x="year",
        y=y_measure,
        color="country",
        markers=True,
        labels={"year": "Год", y_measure: labels[y_measure], "country": "Страна"},
        hover_data={"year": True, y_measure: ":,.2f"},
        title=labels[y_measure]
    )
    fig.add_vline(
        x=selected_year,
        line_width=2,
        line_dash="dash",
        line_color="#2563EB",
        annotation_text=f"Кросс-фильтр: {selected_year}",
        annotation_position="top"
    )
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend_title_text="Страна",
        margin=dict(l=40, r=20, t=70, b=40)
    )
    return fig


#    КЛИК ПО ЛИНИИ -> ГОД ОБЩЕГО ФИЛЬТРА
@callback(
    Output("year-filter", "value"),
    Input("line-chart", "clickData"),
    prevent_initial_call=True
)
def year_from_line_click(click_data):
    if not click_data or not click_data.get("points"):
        return no_update

    clicked_year = int(round(float(click_data["points"][0]["x"])))
    if clicked_year in years:
        return clicked_year

    # На случай, если клик вернул год, отсутствующий в общем списке:
    return min(years, key=lambda y: abs(y - clicked_year))


@callback(
    Output("bubble-chart", "figure"),
    Input("year-filter", "value"),
    Input("bubble-x", "value"),
    Input("bubble-y", "value"),
    Input("bubble-size", "value"),
)
def update_bubble(year, x_measure, y_measure, size_measure):
    dff = df[df["year"] == year].dropna(
        subset=[x_measure, y_measure, size_measure, "continent", "country"]
    ).copy()

    fig = px.scatter(
        dff,
        x=x_measure,
        y=y_measure,
        size=size_measure,
        color="continent",
        hover_name="country",
        size_max=55,
        labels={
            x_measure: labels[x_measure],
            y_measure: labels[y_measure],
            size_measure: labels[size_measure],
            "continent": "Континент"
        },
        title="Пузырьковая диаграмма"
    )
    fig.update_layout(
        template="plotly_white",
        legend_title_text="Континент",
        margin=dict(l=40, r=20, t=70, b=40)
    )
    return fig


@callback(
    Output("top15-chart", "figure"),
    Output("continent-pie", "figure"),
    Input("year-filter", "value"),
)
def update_year_dependent_charts(year):
    dff = df[df["year"] == year].copy()

    top15 = (
        dff.nlargest(15, "pop")
        .sort_values("pop", ascending=True)
    )
    fig_top = px.bar(
        top15,
        x="pop",
        y="country",
        orientation="h",
        color="continent",
        labels={"pop": "Население", "country": "Страна", "continent": "Континент"},
        title="Топ-15 стран по населению"
    )
    fig_top.update_layout(
        template="plotly_white",
        showlegend=False,
        margin=dict(l=40, r=20, t=70, b=40)
    )

    by_continent = (
        dff.groupby("continent", as_index=False)["pop"]
        .sum()
        .sort_values("pop", ascending=False)
    )
    fig_pie = px.pie(
        by_continent,
        names="continent",
        values="pop",
        hole=0.38,
        title="Население по континентам"
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=70, b=30),
        showlegend=False
    )

    return fig_top, fig_pie


if __name__ == "__main__":
    # В обычном Python / Render:
    app.run(debug=False)
