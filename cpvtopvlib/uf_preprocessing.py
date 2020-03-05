
import numpy as np
from sklearn import linear_model
from sklearn.metrics import mean_squared_error
import math
import pandas as pd

from cpvtopvlib import cpvsystem




def calc_uf_lines(x, y, datatype = 'airmass', limit = 200):
    """
    Calculates the parameters of two regression lines for a utilization factor
    specified by datatype.

    Parameters
    ----------
    x : list or numpy.array of float

    y : list or numpy.array of float

    datatype : string
        indicates the type of parameter contained in x.

    limit : numeric, optional
        forces the limit between the regression lines.

    Returns
    -------
    m_low : numeric
        inclination of the first regression line of the utilization factor.

    n_low : numeric
        ordinate at the origin of the first regression line.

    m_high : numeric
        inclination of the second regression line of the utilization factor.

    n_high : numeric
        ordinate at the origin of the second regression line.

    thld : numeric
        limit between the two regression lines of the utilization factor.
    """

    if datatype == 'airmass':
        return calc_two_regression_lines(x, y, limit)

    elif datatype == 'temp_air':
        m_low, n_low, rmsd_low = calc_regression_line(x, y)
        n_high = m_low * limit + n_low
        return m_low, n_low, 0, n_high, limit

    else:
        return 0, 0, 0, 0, 0


def calc_two_regression_lines(x, y, limit = 200):
    """
    Calculates the parameters of two regression lines for the composed
    utilization factors.

    Parameters
    ----------
    x : list or numpy.array of float

    y : list or numpy.array of float

    limit : numeric, optional
        forces the limit between the regression lines.

    Returns
    -------
    m_low : numeric
        inclination of the first regression line of the utilization factor.

    n_low : numeric
        ordinate at the origin of the first regression line.

    m_high : numeric
        inclination of the second regression line of the utilization factor.

    n_high : numeric
        ordinate at the origin of the second regression line.

    thld : numeric
        limit between the two regression lines of the utilization factor.
    """

    # Auxiliar variables initialization.
    x_aux1 = []
    x_aux2 = []

    y_aux1 = []
    y_aux2 = []

    if limit == 200:
        m_low, n_low, m_high, n_high, thld = 0, 0, 0, 0, 0
        rmsd = 10000

        # The x array is traversed in order to find the most fitting
        # regression lines.
        for i in np.arange(1.5, 7.5, 0.1):
            # The original measurements are divided into two sets by the limit.
            for j in range(len(x)):
                if x[j] < i:
                    x_aux1.append(x[j])
                    y_aux1.append(y[j])
                else:
                    x_aux2.append(x[j])
                    y_aux2.append(y[j])

            # Regression lines are calculated for the two sets.
            m_low_temp, n_low_temp, rmsd_low_temp = calc_regression_line(
                x_aux1, y_aux1)

            m_high_temp, n_high_temp, rmsd_high_temp = calc_regression_line(
                x_aux2, y_aux2)

            # Less suitable regression lines are rejected.
            rmsd_temp = rmsd_low_temp + rmsd_high_temp

            if rmsd_temp < rmsd:
                m_low = m_low_temp
                n_low = n_low_temp
                m_high = m_high_temp
                n_high = n_high_temp
                rmsd = rmsd_temp

        # The intersection between the two final regression lines is calculated.
        thld = (n_high - n_low) / (m_low - m_high)

    else:
        # The original measurements are divided into two sets by the limit.
        for j in range(len(x)):
            if x[j] < limit:
                x_aux1.append(x[j])
                y_aux1.append(y[j])
            else:
                x_aux2.append(x[j])
                y_aux2.append(y[j])

        # Regression lines are calculated for the two sets.
        m_low, n_low, rmsd_low = calc_regression_line(x_aux1, y_aux1)

        m_high, n_high, rmsd_high = calc_regression_line(x_aux2, y_aux2)

        # The intersection between the two final regression lines is
        # calculated as it can not be exactly the limit forced.
        thld = (n_high - n_low) / (m_low - m_high)

    return m_low, n_low, m_high, n_high, thld


def calc_regression_line(x, y):
    """
    Wrapper for regression line calcs.

    Parameters
    ----------
    x : array of numbers

    y : array of numbers

    Returns
    -------
    m : numeric
        inclination of the regression line.

    n : numeric
        ordinate at the origin of the regression line.

    rmsd : numeric
        root-mean-square deviation between the regression line and the
        measurements.
    """

    # Initial input treatment.
    if not isinstance(x, np.ndarray):
        x = np.array(x)
    x = x[:, np.newaxis]

    if not isinstance(y, np.ndarray):
        y = np.array(y)
    y = y[:, np.newaxis]

    # The regression line model is executed.
    model = linear_model.LinearRegression()
    model.fit(x, y)

    # Coeficients of the line are obtained.
    m = model.coef_[0][0]

    n = model.intercept_[0]

    # The root-mean-square deviation is calculated.
    y_pred = model.predict(x)

    rmsd = math.sqrt(mean_squared_error(y, y_pred))

    return m, n, rmsd


def calculate_UF(data, filter=False, plot_UF=True):

    if filter == True:
        mean_am=data['relative_airmass'].mean()
        airmass = data[(data['relative_airmass'] >= mean_am-0.1) & (df['relative_airmass'] < mean_am+0.1)]
        mean_temp=data['temp'].mean()
        temperature= data[(data['temp'] >= mean_temp-2.5) & (df['temp'] < mean_temp+2.5)]
        power=data['Isc/DNI']

    else:
        power = data['Isc/DNI']
        airmass = data['relative_airmass']
        temperature = data['temp']

    new_data = pd.DataFrame()
    new_data['airmass'] = airmass
    new_data['temp']=temperature
    new_data['Isc/DNI'] = power

    median_df=pd.Series()
    for j in np.arange(1, 5, 0.1):
        am_data=new_data[(new_data['airmass'] > j - 0.05) & (new_data['airmass'] > j + 0.05)]
        median_df[j]=am_data['Isc/DNI'].median()
        median_Isc=median_df.tolist()


    m_low_am, n_low_am, m_high_am, n_high_am, thld_am = calc_two_regression_lines(
        median_df.index,
        median_Isc, limit=4.0)

    x = np.arange(1, 8, 0.1)
    y1 = m_low_am * x + n_low_am
    y2 = m_high_am * x + n_high_am



    if plot_UF == True:
        import matplotlib.pyplot as plt
        plt.plot(airmass, power, 'b.', median_df.index, median_df, 'r.', x, y1, 'g', x, y2, 'r')
        plt.xlabel("Airmass")
        plt.ylabel("Isc/DNI")
        plt.show()

        IscDNI_top=0.96/1000
        print("thld_am = ", thld_am, '\n'
                                  'm_low_am = ', m_low_am / IscDNI_top, '\n'
                                                                     'm_high_am = ',
              m_high_am / IscDNI_top)

    uf_am=pd.Series()
    for i, row in data.iterrows():
        uf_am[i]=get_single_util_factor(row['relative_airmass'], thld_am,
                                                m_low_am/IscDNI_top, m_high_am/IscDNI_top)

    # Carga y Procesado de Datos sin influencia de la Masa de Aire

    m_low_temp, n_low_temp, m_high_temp, n_high_temp, thld_temp = calc_uf_lines(temperature,
                                                           power,
                                                           datatype='temp_air')
    x = np.arange(0, 25, 1)
    y1 = m_low_temp * x + n_low_temp

    #calculate median for each temperature
    Isc_median_temp = data.groupby([data['temp']]).median()


    if plot_UF == True:
        plt.plot(temperature , power, 'g.', x, y1, 'b')
        plt.xlabel("Temperature")
        plt.ylabel("Isc/DNI")
        plt.show()

    print("thld_temp = ", thld_temp, '\n'
                                'm_low_temp = ', m_low_temp / IscDNI_top, '\n'
                                                                     'm_high_temp = ',
          m_high_temp / IscDNI_top)

    uf_temp = pd.Series()
    for i, row in data.iterrows():
        uf_temp[i]=cpvsystem.get_simple_util_factor(row['temp'], thld_temp,
                                                m_low_temp/ IscDNI_top, m_high_temp/ IscDNI_top)


    return (uf_am, uf_temp)