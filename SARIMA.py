import numpy as np
import pmdarima as pm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from plot_functions import plot_SARIMA_predicition, plot_diagnostic
from utility_functions import RMSE


def run_SARIMA(number_of_measurements, museum_visitors, extended_dates, periods_to_forecast):
    print("---------------SARIMA---------------")
    cutpoint = int(0.7 * number_of_measurements)
    train_set = museum_visitors.Visitors[:cutpoint]
    test_set = museum_visitors.Visitors[cutpoint:]
    xfore = np.linspace(number_of_measurements, number_of_measurements - 1 + periods_to_forecast, periods_to_forecast)

    auto_m = pm.auto_arima(train_set, start_p=0, max_p=12, start_q=0, max_q=12,
                           start_P=0, max_P=2, start_Q=0, max_Q=2, m=12, stepwise=False,
                           seasonal=True, trace=False, error_action="ignore", suppress_warnings=True)

    print("Valori trovati con auto_arima:\n"
          "(p,d,q): {0}\n"
          "(P,D,Q,m): {1}".format(auto_m.order, auto_m.seasonal_order))

    sarima_m = SARIMAX(train_set, order=auto_m.order, seasonal_order=auto_m.seasonal_order)
    sarima_fit_m = sarima_m.fit(disp=False, maxiter=100)

    # plot_diagnostic(sarima_fit_m)

    ypred = sarima_fit_m.predict(start=1, end=len(train_set))
    forecast = sarima_fit_m.get_forecast(steps=len(test_set) + periods_to_forecast)
    yfore = forecast.predicted_mean

    print("La loss del modello SARIMA è:")
    trainscore = RMSE(train_set, ypred)
    print("RMSE train: {}".format(round(trainscore, 3)))
    testscore = RMSE(test_set, yfore[:periods_to_forecast-1])
    print("RMSE test: {}".format(round(testscore, 3)))

    plot_SARIMA_predicition(extended_dates, xfore, yfore, ypred, forecast.conf_int(), cutpoint,
                            periods_to_forecast, museum_visitors)
