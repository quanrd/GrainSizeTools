# ============================================================================ #
#                                                                              #
#    GrainSizeTools Script                                                     #
#    A Python script for characterizing grain size from thin sections          #
#                                                                              #
#    Copyright (c) 2014-present   Marco A. Lopez-Sanchez                       #
#                                                                              #
#    Licensed under the Apache License, Version 2.0 (the "License");           #
#    you may not use this file except in compliance with the License.          #
#    You may obtain a copy of the License at                                   #
#                                                                              #
#        http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS,         #
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#    See the License for the specific language governing permissions and       #
#    limitations under the License.                                            #
#                                                                              #
#    Version 2.0.1                                                             #
#    For details see: http://marcoalopez.github.io/GrainSizeTools/             #
#    download at https://github.com/marcoalopez/GrainSizeTools/releases        #
#                                                                              #
#    Requirements:                                                             #
#        Python version 3.5.x or higher                                        #
#        Numpy version 1.11 or higher                                          #
#        Matplotlib version 1.5.3 or higher                                    #
#        Scipy version 0.13 or higher                                          #
#        Pandas version 0.16.x or higher                                       #
#                                                                              #
# ============================================================================ #

import plots as plots
import tools as tools
from piezometers import quartz, olivine, calcite, feldspar
import numpy as np
from numpy import mean, sqrt, exp, log, log10, array, tan, arctan, delete
from pandas import read_table, read_csv, read_excel, DataFrame
from scipy.stats import sem, t


def extract_column(file_path='auto', col_name='Area'):
    """ Extract the data corresponding to a specific column in tabular-like
    text files generated by the ImageJ or similar applications. Files can be
    in plain text (.txt, .csv) or excel (.xlsx) format

    Parameters
    ----------
    file_path : string, optional
        the file location in quotes, e.g: 'C:/.../nameOfTheFile.csv'
        If 'auto' the function will ask you for the location of the file
        through a file selection dialog.

    col_name : string, optional
        the name of the column to extract. 'Area' by default.

    Examples
    --------
    my_data = extract_column()
    areas = extract_column(col_name='diameters')

    Call function
    -------------
    - get_filepath (tools)

    Returns
    -------
    An array with the column extracted
    """

    if file_path == 'auto':
        file_path = tools.get_filepath()

    if file_path.endswith('.txt'):
        data_frame = read_table(file_path)
        data_set = array(data_frame[col_name])

    elif file_path.endswith('.csv'):
        data_frame = read_csv(file_path)
        data_set = array(data_frame[col_name])

    elif file_path.endswith('.xlsx'):
        data_frame = read_excel(file_path)
        data_set = array(data_frame[col_name])

    else:
        raise TypeError("Error: The file is not a 'txt', 'csv' or 'xlsx' or the file extension was not specified.")

    print(' ')
    print(data_frame.head())
    print(data_frame.tail())
    print(' ')
    print('column extracted:')
    print('{name} = {data}' .format(name=col_name, data=data_set))
    print('n =', len(data_set))
    print(' ')

    return data_set


def area2diameter(areas, correct_diameter=None):
    """ Calculate the equivalent cirular diameter from sectional areas.

    Parameters
    ----------
    areas : array_like
        the sectional areas of the grains

    correct_diameter : None or positive scalar, optional
        add the width of the grain boundaries to correct the diameters. If
        correct_diameter is not declared no correction is considered.

    Returns
    -------
    A numpy array with the equivalent circular diameters
    """

    # calculate the equivalent circular diameter
    diameters = 2 * sqrt(areas / np.pi)

    # diameter correction adding edges (if applicable)
    if correct_diameter is not None:
        diameters += correct_diameter

    return diameters


def calc_grain_size(diameters, areas=None, plot='lin', binsize='auto', bandwidth='silverman'):
    """ Estimate different 1D measures of grain size from a population
    grain sections and plot the location of these measures along with
    the apparent grain size distribution. Includes the arithmetic mean,
    the area-weighted mean, the median, and the frequency peak grain
    sizes.

    Parameters
    ----------
    diameters : array_like
        the apparent diameters of the grains

    areas : array_like or None, optional
        the areas of the grain profiles

    plot : string, optional
        the scale/type of the plot and grain size estimation.

        | Types:
        | 'lin' frequency vs linear diameter distribution
        | 'log' frequency vs logarithmic (base e) diameter distribution
        | 'log10' frequency vs logarithmic (base 10) diameter distribution
        | 'sqrt' frequency vs square root diameter distribution
        | 'area' area-weighted frequency vs diameter distribution
        | 'norm' normalized grain size distribution

    binsize : string or positive scalar, optional
        If 'auto', it defines the plug-in method to calculate the bin size.
        When integer or float, it directly specifies the bin size.
        Default: the 'auto' method.

        | Available plug-in methods:
        | 'auto' (fd if sample_size > 1000 or Sturges otherwise)
        | 'doane' (Doane's rule)
        | 'fd' (Freedman-Diaconis rule)
        | 'rice' (Rice's rule)
        | 'scott' (Scott rule)
        | 'sqrt' (square-root rule)
        | 'sturges' (Sturge's rule)

    bandwidth : string {'silverman' or 'scott'} or positive scalar, optional
        the method to estimate the bandwidth or a scalar directly defining the
        bandwidth. It uses the Silverman plug-in method by default.

    Call functions
    --------------
    - calc_freq_grainsize (tools)
    - calc_areaweighted_grainsize (tools)
    - norm_grain_size (tools)

    Examples
    --------
    calc_grain_size(diameters)
    calc_grain_size(diameters, plot='log')
    calc_grain_size(diameters, areas, plot='area')
    calc_grain_size(diameters, binsize='doane', bandwidth=0.5)

    Returns
    -------
    A plot with the distribution of apparent grain sizes and several
    statistical parameters
    """

    # determine the grain size parameters using number-weighted approaches
    if plot == 'lin':
        return tools.calc_freq_grainsize(diameters, binsize, plot='linear', bandwidth=bandwidth)

    elif plot == 'log':
        diameters = log(diameters)
        return tools.calc_freq_grainsize(diameters, binsize, plot='log', bandwidth=bandwidth)

    elif plot == 'log10':
        diameters = log10(diameters)
        return tools.calc_freq_grainsize(diameters, binsize, plot='log10', bandwidth=bandwidth)

    elif plot == 'norm':
        diameters = tools.norm_grain_size(diameters, bandwidth=bandwidth, binsize=binsize)
        return tools.calc_freq_grainsize(diameters, binsize, plot='norm', bandwidth=bandwidth)

    elif plot == 'sqrt':
        diameters = sqrt(diameters)
        return tools.calc_freq_grainsize(diameters, binsize, plot='sqrt', bandwidth=bandwidth)

    # determine the grain size using the area-weighted approach
    elif plot == 'area':
        if areas is None:
            print('You must provide the areas of the grain sections')
            return None
        else:
            return tools.calc_areaweighted_grainsize(areas, diameters, binsize)

    else:
        raise ValueError("The type of plot has been misspelled, please use 'lin', 'log', 'log10', sqrt', 'norm', or 'area'")


def Saltykov(diameters, numbins=10, calc_vol=None, text_file=None, return_data=False, left_edge=0):
    """ Estimate the actual (3D) distribution of grain size from the population of
    apparent diameters measured in a thin section using the Saltykov method.
    (Saltykov 1967; Sahagian and Proussevitch 1998).

    The Saltykov method is optimal to estimate the volume of a particular grain size
    fraction as well as to obtain a qualitative view of the appearance of the actual
    3D grain size population, either in uni- or multimodal populations.

    Parameters
    ----------
    diameters : array_like
        the apparent diameters of the grains

    numbins : positive integer, optional
        the number of bins/classes of the histrogram. If not declared, is set
        to 10 by default

    calc_vol : positive scalar or None, optional
        if the user specifies a number, the function will return the volume
        occupied by the grain fraction up to that value.

    text_file : string or None, optional
        if the user specifies a name, the function will return a csv file
        with that name containing the data used to construct the Saltykov
        plot

    return_data : bool, optional
       if True the function will return the position of the midpoints and
       the frequencies (use by other functions).

    left_edge : positive scalar or 'min', optional
        set the left edge of the histogram.

    Call functions
    --------------
    - unfold_population (tools)
    - Saltykov_plot (plots)

    References
    ----------
    | Saltykov SA (1967) http://doi.org/10.1007/978-3-642-88260-9_31
    | Sahagian and Proussevitch (1998) https://doi.org/10.1016/S0377-0273(98)00043-2

    Return
    ------
    Statistical descriptors, a plot, and a file with the data (optional)
    """

    if isinstance(numbins, int) is False:
        raise ValueError('Numbins must be a positive integer')
    if numbins <= 0:
        raise ValueError('Numbins must be higher than zero')
    if isinstance(left_edge, (int, float)):
        if left_edge < 0:
            raise ValueError("left_edge must be a positive scalar or 'min'")

    # compute the histogram
    if left_edge == 'min':
        freq, bin_edges = np.histogram(diameters, bins=numbins, range=(diameters.min(), diameters.max()), density=True)
    else:
        freq, bin_edges = np.histogram(diameters, bins=numbins, range=(left_edge, diameters.max()), density=True)
    binsize = bin_edges[1] - bin_edges[0]

    # Create an array with the left edges of the bins and other with the midpoints
    left_edges = delete(bin_edges, -1)
    mid_points = left_edges + binsize / 2

    # Unfold the population of apparent diameters using the Scheil-Schwartz-Saltykov method
    freq3D = tools.unfold_population(freq, bin_edges, binsize, mid_points)

    # Calculate the volume-weighted cumulative frequency distribution
    x_vol = binsize * (4 / 3.) * np.pi * (mid_points**3)
    freq_vol = x_vol * freq3D
    cdf = np.cumsum(freq_vol)
    cdf_norm = 100 * (cdf / cdf[-1])

    # Estimate the volume of a particular grain size fraction (if proceed)
    if calc_vol is not None:
        x, y = mid_points, cdf_norm
        index = np.argmax(mid_points > calc_vol)
        angle = arctan((y[index] - y[index - 1]) / (x[index] - x[index - 1]))
        volume = y[index - 1] + tan(angle) * (calc_vol - x[index - 1])
        if volume < 100.0:
            print(' ')
            print('volume fraction (up to', calc_vol, 'microns) =', round(volume, 2), '%')
        else:
            print(' ')
            print('volume fraction (up to', calc_vol, 'microns) =', 100, '%')

    # Create a text file with the midpoints, class frequencies, and cumulative volumes (if apply)
    if text_file is not None:
        if isinstance(text_file, str) is False:
            print('text_file must be None or a string')
        df = DataFrame({'mid_points': np.around(mid_points, 3),
                        'freqs': np.around(freq3D, 4),
                        'cum_vol': np.around(cdf_norm, 2)})
        if text_file.endswith('.txt'):
            df.to_csv(text_file, sep='\t')
        elif text_file.endswith('.csv'):
            df.to_csv(text_file)
        else:
            raise ValueError('text file must be specified as .csv or .txt')
        print(' ')
        print('The file {} was created' .format(text_file))

    # return data or figure (if apply)
    if return_data is True:
        return mid_points, freq3D

    elif return_data is False:
        print('bin size =', round(binsize, 2))
        return plots.Saltykov_plot(left_edges, freq3D, binsize, mid_points, cdf_norm)

    else:
        raise TypeError('return_data must be set as True or False')


def calc_shape(diameters, class_range=(10, 20), initial_guess=False):
    """ Estimates the shape of the actual (3D) distribution of grain size from a
    population of apparent diameters measured in a thin section using the two-step
    method (Lopez-Sanchez and Llana-Funez, 2016).

    The method only works properly for unimodal lognormal-like grain size populations
    and returns the MSD (i.e. shape) and the median (i.e. scale) values, which
    describe the lognormal population of grain sizes at their lineal scale. For
    details see Lopez-Sanchez and Llana-Funez (2016).

    Parameters
    ----------
    diameters : array_like
        the apparent diameters of the grains

    class_range : tupe or list with two values, optional
        the range of classes considered. The algorithm will estimate the optimal
        number of classes within this range.

    initial_guess : boolean, optional
        If False, the script will use the default guessing values to fit a
        lognormal distribution. If True, the script will ask the user to define
        their own MSD and median guessing values.

    Call functions
    --------------
    - Saltykov
    - fit_log (tools)
    - twostep_plot (plots)

    References
    ----------
    | Saltykov SA (1967) http://doi.org/10.1007/978-3-642-88260-9_31
    | Sahagian and Proussevitch (1998) https://doi.org/10.1016/S0377-0273(98)00043-2
    | Lopez-Sanchez and Llana-Funez (2016) https://doi.org/10.1016/j.jsg.2016.10.008

    Returns
    -------
    A plot with an estimate of the actual (3D) grains size distribution and
    several statistical parameters
    """

    if initial_guess is False:
        shape = 1.2
        scale = 35.0
    elif initial_guess is True:
        shape = float(input('Define an initial guess for the MSD parameter (the default value is 1.2; MSD > 1.0): '))
        scale = float(input('Define an initial guess for the geometric mean (the default value is 35.0): '))
    else:
        raise TypeError('Initial_guess must be set as True or False')

    # estimate the number of classes that produces the best fit within the range defined
    class_list = list(range(class_range[0], class_range[1] + 1))
    stds = np.zeros(len(class_list))

    for index, item in enumerate(class_list):
        mid_points, frequencies = Saltykov(diameters, numbins=item, return_data=True)
        optimal_params, sigma_error = tools.fit_log(mid_points, frequencies, initial_guess=(shape, scale))
        stds[index] = sigma_error[0]

    optimal_num_classes = class_list[np.argmin(stds)]
    mid_points, frequencies = Saltykov(diameters, numbins=optimal_num_classes, return_data=True)
    optimal_params, sigma_err = tools.fit_log(mid_points, frequencies, (shape, scale))

    print(' ')
    print('OPTIMAL VALUES')
    print('Number of clasess: {}' .format(optimal_num_classes))
    print('MSD (shape) = {msd} ± {err}' .format(msd=round(optimal_params[0], 2),
                                                err=round(3 * sigma_err[0], 2)))
    print('Geometric mean (location) = {gmean} ± {err}' .format(gmean=round(optimal_params[1], 2),
                                                                err=round(3 * sigma_err[1], 2)))
    print(' ')
    # print(' Covariance matrix:\n', covm)

    # prepare data for the plot
    xgrid = tools.gen_xgrid(diameters, 0.1, max(diameters))
    best_fit = tools.log_function(xgrid, optimal_params[0], optimal_params[1])

    # Estimate all the combinatorial posibilities for fit curves taking into account the uncertainties
    values = array([tools.log_function(xgrid, optimal_params[0] + sigma_err[0], optimal_params[1] + sigma_err[1]),
                    tools.log_function(xgrid, optimal_params[0] - sigma_err[0], optimal_params[1] - sigma_err[1]),
                    tools.log_function(xgrid, optimal_params[0] + sigma_err[0], optimal_params[1] - sigma_err[1]),
                    tools.log_function(xgrid, optimal_params[0] - sigma_err[0], optimal_params[1] + sigma_err[1])])

    # Estimate the standard deviation of the all values obtained
    fit_error = np.std(values, axis=0)

    return plots.twostep_plot(xgrid, mid_points, frequencies, best_fit, fit_error)


def confidence_interval(data, confidence=0.95):
    """Estimate the confidence interval using the t-distribution with n-1
    degrees of freedom t(n-1). This is the way to go when sample size is
    small and the standard deviation cannot be estimated accurately. For
    large datasets, the t-distribution approaches the normal distribution.

    Parameters
    ----------
    data : array-like
        the dataset

    confidence : float between 0 and 1, optional
        the confidence interval, default = 0.95

    Assumptions
    -----------
    the data follows a normal distrubution (when sample size is large)

    call_functions
    --------------
    Scipy's t.interval

    Returns
    -------
    None
    """
    degrees_freedom = len(data) - 1
    sample_mean = mean(data)
    sd_err = sem(data)  # Standard error of the mean SD / sqrt(n)
    low, high = t.interval(confidence, degrees_freedom, sample_mean, sd_err)
    err = high - sample_mean

    print(' ')
    print('Confidence set at {} %' .format(confidence * 100))
    print('Mean = {mean} ± {err}' .format(mean=round(sample_mean, 2), err=round(err, 2)))
    print('Max / min = {max} / {min}' .format(max=round(high, 2), min=round(low, 2)))
    print('Coefficient of variation = {} %' .format(round(100 * err / sample_mean, 1)))

    return None


def calc_diffstress(grain_size, phase, piezometer, correction=False):
    """ Apply different piezometric relations to estimate the differential
    stress from average apparent grain sizes. The piezometric relation has
    the following general form:

    df = B * grain_size**-m

    where df is the differential stress in [MPa], B is an experimentally
    derived parameter in [MPa micron**m], grain_size is the aparent grain
    size in [microns], and m is an experimentally derived exponent.

    Parameters
    ----------
    grain_size : positive scalar
        the apparent grain size in microns

    phase : string {'quartz', 'olivine', 'calcite', or 'feldspar'}
        the mineral phase

    piezometer : string
        the piezometric relation to be use

    correction : bool, default False
        correct the stress values for plane stress (Behr & Platt, 2013)

     References
    -----------
    Berh and Platt (2013) https://doi.org/10.1016/J.JSG.2013.07.
    De Hoff and Rhines (1968) Quantitative Microscopy. Mcgraw-Hill. New York.

    Call functions
    --------------
    quartz, olivine, calcite, and albite from piezometers.py

    Assumptions
    -----------
    - Independence of temperature (excepting Shimizu piezometer), total strain,
    flow stress, and water content.
    - Recrystallized grains are equidimensional or close to equidimensional when
    using a single section.
    - The piezometer relations requires entering the grain size as "average"
    apparent grain size values calculated using equivalent circular diameters
    (ECD) with no stereological correction. See documentation for more details.
    - When required, the grain size value will be converted from ECD to linear
    intercept (LI) using a correction factor based on De Hoff and Rhines (1968):
    LI = (correction factor / sqrt(4/pi)) * ECD
    - Stress estimates can be corrected from uniaxial compression (experiments)
    to plane strain (nature) multiplying the estimate of th epaleopiezometer by
    2/sqrt(3) (Behr and Platt, 2013)


    Returns
    -------
    The differential stress in MPa (a float)
    """

    if phase == 'quartz':
        B, m, warn, linear_interceps, correction_factor = quartz(piezometer)
    elif phase == 'olivine':
        B, m, warn, linear_interceps, correction_factor = olivine(piezometer)
    elif phase == 'calcite':
        B, m, warn, linear_interceps, correction_factor = calcite(piezometer)
    elif phase == 'feldspar':
        B, m, warn, linear_interceps, correction_factor = feldspar(piezometer)
    else:
        raise ValueError('Phase name misspelled. Please choose between valid mineral names')

    # Special cases (convert from ECD to linear intercepts)
    if linear_interceps is True:
        grain_size = (correction_factor / (sqrt(4 / np.pi))) * grain_size

    # Estimate differential stress
    if piezometer == 'Shimizu':
        T = float(input("Please, enter the temperature [in C degrees] during deformation: "))
        diff_stress = B * grain_size**(-m) * exp(698 / (T + 273.15))
        if correction is True:
            diff_stress = diff_stress * 2 / sqrt(3)
        print(' ')
        print('differential stress = {} MPa' .format(round(diff_stress, 2)))
        print(warn)
    else:
        diff_stress = B * grain_size**-m
        if correction is True:
            diff_stress = diff_stress * 2 / sqrt(3)
        print(' ')
        print('differential stress = {} MPa' .format(round(diff_stress, 2)))
        print(warn)
        print(' ')

    return None


welcome = """
======================================================================================
Welcome to GrainSizeTools script v2.0.1
======================================================================================
GrainSizeTools is a free open-source cross-platform script to visualize and characterize
the grain size in polycrystalline materials from thin sections and estimate differential
stresses via paleopizometers.
"""
functions_list = """
METHODS AVAILABLE
==================  ==================================================================
List of functions   Description
==================  ==================================================================
area2diameter       Estimate the equivalent circular diameter from area sections
calc_diffstress     Estimate diff. stress from grain size using piezometers
calc_grain_size     Estimate the apparent grain size and visualize their distribution
calc_shape          Characterize the log shape of the actual grain size distribution
confidence_interval Estimate a robust confidence interval using the t-distribution
extract_column      Extract data from tabular-like text files (txt, csv or xlsx)
Saltykov            Estimate the actual grain size distribution via the Saltykov method
==================  ==================================================================

You can get more information about the methods in the following ways:
    (1) Typing help plus the name of the function e.g. help(calc_shape)
    (2) In the Spyder IDE by writing the name of the function and clicking Ctrl + I
    (3) Visiting the script documentation at https://marcoalopez.github.io/GrainSizeTools/
    (4) Get a list of the methods available: print(functions_list)
"""

print(welcome)
print(functions_list)

if float(np.__version__[0:4]) < 1.11:
    print('The installed Numpy version', np.__version__, 'is too old.')
    print('Please upgrade to v1.11 or higher')

# ============================================================================ #
# Make it correct, make it clear, make it concise, make it fast. In that order.#
#                                                                     Wes Dyer #
# ============================================================================ #
