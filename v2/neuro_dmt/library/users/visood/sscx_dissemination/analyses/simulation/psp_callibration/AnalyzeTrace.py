# Natali Barros Zulaica
# Feb 2018

# This is a package to analyze the classic TM traces

import numpy as np
import scipy
from scipy import signal
from math import factorial
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# --------- THESE TWO FUNCTIONS ARE USED TO COMPUTE TAU_MEM FROM RECOVERY PEAK ----------------
def func(x, a, b, c):
    x = x - x.min()
    return a * (1 - np.exp(-b * x)) + c

def compute_TauMem(x, y):
    popt, pcov = curve_fit(func, x, y)
    Tau_mem = (1/popt[1])/100.0 #ms
    return popt, pcov, func, Tau_mem
# -----------------------------------------------------------------------------------------------

def amp_rise_lat_firstEPSP(sample_connection, STIM_TIMES, time, t_wind_bef, t_wind_aft, pre_AP, PLOT = False):
    """
    This function selects the rise curve (first EPSP) and find the  5, 20 and 80 % of the amplitude.
    Firstly computes the amplitude as the difference minimum - maximum in the interval (first_stimulus, max_peak).
    Secondly computes the percentages and find the times for these respective values.
    Tau_rise = 80%_time - 20%_time (Feldmeyer et al., 1999)
    latency = 5%_time - first_stimulus
    :param sample_connection: array with voltage traces oriented (voltage vs trials)(row vs column)
    :param STIM_TIMES: list with the stimuli points
    :param time: list with time steps in s
    :param t_wind_aft: time window to compute max and min
    :return amp_value: list with amplitude values in the same units as sample_connection.
    Computed as the difference between the 20 and the 80 % of the first EPSP rise part
    :return TAU_rise: list with tau_rise values in ms. Computed as the distance between the times when
    the 20 and 80 % of the rise part for the first EPSP happens
    :return latency: list with latency values in ms. Computed as the time between the AP of the presynaptic cell
    and the 5% of the first EPSP
    """
    # The analysis are performed over the mean trace
    conn = np.mean(sample_connection, axis=0)

    # save only the trace part for the first peak for voltage and time
    rise_curve = conn[STIM_TIMES[0] - t_wind_bef:STIM_TIMES[0] + t_wind_aft]
    rise_curve_time = time[STIM_TIMES[0] - t_wind_bef:STIM_TIMES[0] + t_wind_aft]

    # find max, min and compute amplitude
    max_value = np.max(rise_curve)
    min_value = np.min(rise_curve)
    amp_value_total = np.abs(max_value - min_value)

    # compute percentages
    twenty_peak_value = amp_value_total * 80.0 / 100.0
    eighty_peak_value = amp_value_total * 20.0 / 100.0
    five_peak_value = amp_value_total * 95.0 / 100.0
    amp_value = eighty_peak_value - twenty_peak_value

    # Find the exact voltage point
    twenty_curve_value = -(twenty_peak_value - max_value)
    eighty_curve_value = -(eighty_peak_value - max_value)
    five_curve_value = -(five_peak_value - max_value)

    # Find time point for the minimum
    for x, s in zip(rise_curve, rise_curve_time):
        if (x == min_value):
            min_time = s

    # Find time points for the 5, 20 and 80 % of the first EPSP
    n = 0
    m = 0
    l = 0
    for i, j in zip(rise_curve, rise_curve_time):
        if (n == 0) and (i > twenty_curve_value) and (j > min_time):
            twenty_time = j
            n = 1
        if (m == 0) and (i > eighty_curve_value) and (j > min_time):
            eighty_time = j
            m = 1
        if (l == 0) and (i > five_curve_value) and (j > min_time):
            five_time = j
            l = 1

    TAU_rise = (twenty_time-eighty_time)*1000.0
    latency = (five_time-pre_AP)*1000.0

    # PLOT first EPSP with the computed points for the 5, 20 and 80 % of the first EPSP
    if PLOT == True:
        plt.figure()
        plt.plot(rise_curve_time, rise_curve, label='first EPSP')
        plt.plot(twenty_time, twenty_curve_value, 'ro', label='20%')
        plt.plot(eighty_time, eighty_curve_value, 'mo', label='80%')
        plt.plot(five_time, five_curve_value, 'go', label='5%')
        plt.legend()
        plt.show()

    return amp_value, TAU_rise, latency

def butter_lowpass_filter(data,cutoff,fs,order=5):
    nyq = 0.5 * fs # Nyquist frequency = half of sampling frequency
    normal_cutoff = float(cutoff/nyq) # normal_cutoff = 0.01
    # Design an Nth order digital or analog Butterworth filter and return the filter coefficients in (B,A) form
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = scipy.signal.lfilter(b,a,data)
    return y

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
         The Savitzky-Golay filter removes high frequency noise from data.
         It has the advantage of preserving the original shape and
         features of the signal better than other types of filtering
         approaches, such as moving averages techniques.
         This is an archival dump of old wiki content --- see scipy.org for current material.
         Please see http://scipy-cookbook.readthedocs.org/
         (http://scipy.github.io/old-wiki/pages/Cookbook/SavitzkyGolay)
         Parameters
         ----------
         y : array_like, shape (N,)
             the values of the time history of the signal.
         window_size : int
             the length of the window. Must be an odd integer number.
         order : int
             the order of the polynomial used in the filtering.
             Must be less then `window_size` - 1.
         deriv: int
             the order of the derivative to compute (default = 0 means only smoothing)
         Returns
         -------
         ys : ndarray, shape (N)
             the smoothed signal (or it's n-th derivative).
         Notes
         -----
         The Savitzky-Golay is a type of low-pass filter, particularly
         suited for smoothing noisy data. The main idea behind this
         approach is to make for each point a least-square fit with a
         polynomial of high order over a odd-sized window centered at
         the point.
         Examples
         --------
         t = np.linspace(-4, 4, 500)
         y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
         ysg = savitzky_golay(y, window_size=31, order=4)
         import matplotlib.pyplot as plt
         plt.plot(t, y, label='Noisy signal')
         plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
         plt.plot(t, ysg, 'r', label='Filtered signal')
         plt.legend()
         plt.show()
         References
         ----------
         .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
            Data by Simplified Least Squares Procedures. Analytical
            Chemistry, 1964, 36 (8), pp 1627-1639.
         .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
            W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
            Cambridge University Press ISBN-13: 9780521880688
         """
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')


def deconvolver(mean_trace, Rin, TAU_MEM):
    """
    This function computes the deconvolution of mean trace
    :param mean_trace: data array 1D (list)
    :param TAU_MEM: membrane constant (ms)
    :param Rin:
    :return deconvolved_trace: list with the voltage values for the deconvolved mean_trace
    """
    x = range(len(mean_trace))
    dx = x[1] - x[0]       #dx==1 -> as this is the distance between points in mean_trace, we have to count the time in 10ths of miliseconds (really dx=0.0001)
    print ("derivative...")
    derived_v = np.gradient(mean_trace,dx)

    deconvolved_trace = []
    # DECONVOLVE
    for j in range(len(mean_trace)):
        top = (TAU_MEM*derived_v[j])+mean_trace[j]
        deconvolved_trace.append(top/Rin) # As we normalize the trace we don't care
    return deconvolved_trace


def cropping(deconv_trace, STIM_TIMES, t_wind_bef, t_wind_aft):
    """
    This function computes a baseline for the deconvolved trace
    :param deconv_trace:
    :param STIM_TIMES:
    :param t_wind_bef:
    :param t_wind_aft:
    :return:
    """
    crop1 = deconv_trace[0:STIM_TIMES[0]-t_wind_bef]
    crop2 = deconv_trace[STIM_TIMES[7]+t_wind_aft:STIM_TIMES[8]-t_wind_bef]
    totalcrop = crop1.tolist()+crop2.tolist()
    baseline = np.mean(totalcrop)
    return baseline

def compute_peaks(tmax, dt, deconv_trace, STIM_TIMES, t_wind_aft):
    """
    This function computes the peaks and the times when this peaks occur in the deconv_trace
    :param tmax: total recording time in seconds
    :param dt: sampling time in seconds
    :param deconv_trace: list with deconvolve voltage data
    :param STIM_TIMES: times where a stimulus is performed
    :param t_wind_aft: time window after the stimulus to find the max value
    :return peaks: list with the peak values
    :return peak_time: list with time peaks
    """

    time_array = np.arange(0, tmax, dt)
    #print (time_array)

    peaks = []
    for t in STIM_TIMES:
        pk = np.max(deconv_trace[t:(t + t_wind_aft)])
        peaks.append(pk)

    '''compute peak times'''
    peak_time = []
    for i in range(len(deconv_trace)):
        for m in peaks:
            if deconv_trace[i] == m:
                peak_time.append(time_array[i])
    # x = 0
    # for m in deconv_trace:
    #     if m in peaks and (x > STIM_TIMES[0] and x < STIM_TIMES[0] + t_wind_aft):
    #         while len(peak_time) < 1:
    #             peak_time.append(x / float(STIM_TIMES[8]))
    #     if m in peaks and (x > STIM_TIMES[1] and x < STIM_TIMES[1] + t_wind_aft):
    #         while len(peak_time) < 2:
    #             peak_time.append(x / float(STIM_TIMES[8]))
    #     if m in peaks and (x > STIM_TIMES[2] and x < STIM_TIMES[2] + t_wind_aft):
    #         while len(peak_time) < 3:
    #             peak_time.append(x / float(STIM_TIMES[8]))
    #     if m in peaks and (x > STIM_TIMES[3] and x < STIM_TIMES[3] + t_wind_aft):
    #         while len(peak_time) < 4:
    #             peak_time.append(x / float(STIM_TIMES[8]))
    #     if m in peaks and (x > STIM_TIMES[4] and x < STIM_TIMES[4] + t_wind_aft):
    #         while len(peak_time) < 5:
    #             peak_time.append(x / float(STIM_TIMES[8]))
    #     if m in peaks and (x > STIM_TIMES[5] and x < STIM_TIMES[5] + t_wind_aft):
    #         while len(peak_time) < 6:
    #             peak_time.append(x / float(STIM_TIMES[8]))
    #     if m in peaks and (x > STIM_TIMES[6] and x < STIM_TIMES[6] + t_wind_aft):
    #         while len(peak_time) < 7:
    #             peak_time.append(x / float(STIM_TIMES[8]))
    #     if m in peaks and (x > STIM_TIMES[7] and x < STIM_TIMES[7] + t_wind_aft):
    #         while len(peak_time) < 8:
    #             peak_time.append(x / float(STIM_TIMES[8]))
    #     if m in peaks and (x > STIM_TIMES[8] and x < STIM_TIMES[8] + t_wind_aft):
    #         while len(peak_time) < 9:
    #             peak_time.append(x / float(STIM_TIMES[8]))
    #     else:
    #         pass
    #     x = x + 1
    return peaks, peak_time


def compute_amplitude(deconv_trace, STIM_TIMES, t_wind_bef, t_wind_aft): # t_wind_aft_min
    """
    This function compute the amplitudes of the EPSPs in deconv_trace
    :param deconv_trace: deconvelved voltage data 1D-array (list)
    :param STIM_TIMES: times where a stimulus is performed
    :param t_wind_aft: time window after the stimulus to find the max value
    :return amplitudes: list with amplitude values
    """
    amplitudes = []
    max = []
    min = []
    for t in STIM_TIMES:
        mx = np.max(deconv_trace[(t-t_wind_bef):(t + t_wind_aft)])
        mn = np.min(deconv_trace[(t-t_wind_bef):(t + t_wind_aft)])
        amp = np.abs(mx - mn)
        max.append(mx)#float("{0:.2f}".format(mx)))
        min.append(mn)#float("{0:.2f}".format(mn)))
        amplitudes.append(amp)#(float("{0:.2f}".format(amp)))
    return max, min, amplitudes

def Normalize_trace(trace):
    # normalizing the sweep
    trace_norm = []
    pk_max = np.max(trace)
    pk_min = np.min(trace)
    for z in trace:
        z_uni = (z - pk_min) / (pk_max - pk_min)
        trace_norm.append(z_uni)
    return trace_norm

def Failures(sample_connection, STIM_TIMES, t_wind_bef, t_wind_aft):
    """
    This function computes the failure rate for one cell connection (Markram et al., 1997)
    :param sample_connection:
    :param STIM_TIMES:
    :param t_wind_aft:
    :return:
    """
    trace_num = len(sample_connection)

    # define mean base line fom the mean trace as the mean of all the values from mean trace
    mean_sample = np.mean(sample_connection, axis = 0)
    mean_sam_norm = Normalize_trace(mean_sample)
    mean_baseline = np.mean(mean_sam_norm)

    #compute failures per each sweep
    # create list to save the failure rate
    failure_count = [0,0,0,0,0,0,0,0,0]
    for sweep in sample_connection:
        # normalizing the sweep
        norm_sweep = Normalize_trace(sweep)

        # compute noise as std of amplitudes of small peaks before the first EPSP
        noise = np.std(norm_sweep[50:STIM_TIMES[0]-50])
        failureline = 1.6 * noise + mean_baseline

        max, min, amp = compute_amplitude(norm_sweep, STIM_TIMES, t_wind_bef, t_wind_aft)

        indx = [0,1,2,3,4,5,6,7,8]
        for a, i in zip(max, indx):
            if a <= failureline:
                failure_count[i] = failure_count[i]+1

    failure_percent = []
    for f in failure_count:
        fp = f*100.0/float(trace_num)
        failure_percent.append(fp)

    return failure_percent

def cv_deconv(sample_connection,STIM_TIMES, t_wind_aft_min, t_wind_aft_max, TAU_MEM, fs):
    """
    This function compute the CV profile of the EPSP amplitudes in sample_connection
    This function filters and deconvolve the sweep before computing the amplitudes
    :param sample_connection: array with voltage traces
    :return amp_cv: list with cv values for each PSP
    """
    amp_array = []
    for trace in sample_connection:
        dec_trace = deconvolver(trace,TAU_MEM)
        data = dec_trace-dec_trace[0]
        dec_filter = butter_lowpass_filter(data, 50.0, fs, order=5)
        max, min, amp = compute_amplitude(dec_filter, STIM_TIMES, t_wind_aft_min, t_wind_aft_max)
        amp_array.append(amp)

    ''' compute cv'''
    amp_mean = np.mean(amp_array, axis=0)
    amp_std = np.std(amp_array, axis=0)
    amp_cv = amp_std/amp_mean
    return amp_cv


def cv_JKK(sample_connection, STIM_TIMES, t_wind_aft_min, t_wind_aft_max):
    """ This function computes the Jack Knife (bootstraping) mean traces from a set of traces in sample_connection.
    Also computes the peaks (max values) and minimum of these mean traces and the times for the peaks.
    From the max and min it computes the amplitudes and from amplitudes it computes the CV for each EPSP
    :param sample_connection: data array with all the sweeps of the sample connection
    :param STIM_TIMES: times where a stimulus is performed as time steps (ex: stim1 at 0.1 s; sample_frec = 10KHz -> stim1 = 1000)
    :param t_wind_aft: time window after the stimulus to find the max value (value in time steps)
    :return CV
    """
    # Jackknife bootstraping:
    # make the mean of the traces eliminating each time one, and extract the peaks amplitude for each mean trace
    # the std has to be scaled to (n - 1) as we are resampling in 1/(n - 1) so without scaling the std is very small

    jkk_means = [] # safe EPSP amplitudes from JKK samples
    #n = 0
    for sweep in range(len(sample_connection)):
        # remove one different sweep from the trace set in each iteration and compute the mean
        new_sample = np.delete(sample_connection, sweep, 0)
        jkk_sample = np.mean(new_sample, axis=0)

        # compute amplitudes from jkk_sample
        max, min, amplitudes = compute_amplitude(jkk_sample, STIM_TIMES, t_wind_aft_min, t_wind_aft_max)

        # plt.figure()
        # plt.title('JKK trace')
        # plt.plot(jkk_sample)
        # plt.plot(STIM_TIMES, max, 'ro')
        # plt.plot(STIM_TIMES, min, 'go')
        # plt.show()
        # plt.savefig('/Users/natalibarros/Desktop/test_traces/JKKtrace_%s.pdf' %n)
        # n = n + 1

        jkk_means.append(amplitudes)

    # compute mean
    amp_MEAN = np.mean(jkk_means, axis=0)
    #print ('JKK amp mean', amp_MEAN)


    # compute std - don't use np.std, make the difference
    DIF = []
    for am in jkk_means:
        dif = (am - amp_MEAN)**2
        DIF.append(dif)

    N = np.float(len(sample_connection))
    scale_fact = np.float(N - 1.0)
    amp_std = scale_fact*np.sqrt(np.sum(DIF, axis = 0)/N)
    #print ('JKK amp std', amp_std)

    # N = np.float(len(sample_connection))
    # scale_fact = np.sqrt(N - 1.0)
    # amp_std = scale_fact*np.sqrt(np.sum(DIF, axis = 0))

    # compute CV = std/mean
    CV = amp_std/amp_MEAN

    return amp_MEAN, CV


#### functions for U, D, F fitting ####################
# Ecuations from Maass and Markram 2002

# parenthesis have been removed when changing to python 3.7

x_before = lambda x_last, dep, delta_t: 1.0 - ((1.0 - x_last) * np.exp(-delta_t/dep))

u_before = lambda u_se, u_last, fac, delta_t: u_last * (1.0 - u_se) * np.exp(-delta_t/fac) + u_se

DELTA_T_ARRAY = [0., 50., 50., 50., 50., 50., 50., 50., 550.]  # msec

def compute_fx(u_se, u_last, fac, x_last, dep, delta_t):
    u_spike = u_before(u_se, u_last, fac, delta_t)
    x_spike = x_before(x_last, dep, delta_t)
    #print ('u spike', u_spike)
    #print ('x spike', x_spike)
    spike_amp = u_spike * x_spike
    x_last = x_spike - x_spike * u_spike
    return [spike_amp, u_spike, x_last]

def spike_amplitudes(u_se, fac, dep):
    u_last = 0.0
    x_last = 1.0
    spike_array = []
    for delta_t in DELTA_T_ARRAY:
        spike_amp, u_last, x_last = compute_fx(u_se, u_last, fac, x_last, dep, delta_t)
        spike_array.append(spike_amp)
    return spike_array

def compute_fitness(u_se, fac, dep, experimental):
    spike_array = spike_amplitudes(u_se, fac, dep)
    #print ('sa', spike_array)
    scaled_spike_array = [i/spike_array[0] for i in spike_array]
    #print ('spa', scaled_spike_array)
    distance = [(i - j)**2 for i, j in zip(scaled_spike_array, experimental)]
    return np.mean(distance), scaled_spike_array

