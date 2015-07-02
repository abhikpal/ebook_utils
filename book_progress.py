import re
import datetime
import pylab
from scipy.stats import gaussian_kde

def get_book_list(filename='clippings.txt'):
    """
    Returns a list of all the books for which record can be found in the
    clippings file.

    input:
        filename: name of the clippings file ('clippings.txt')

    output:
        list: of all the books with records in the clippings file.
    """

    book_file = open(filename, 'r')

    book_list = []

    while True:
        try:
            book_line = book_file.next().strip()
            if book_line == '==========':
                current_book = re.search('(.*?)\ \(.*?\)', (book_file.next()))
                current_book_name = current_book.group(1)
                if current_book_name not in book_list:
                    book_list.append(current_book_name)
        except StopIteration:
            break

    return book_list

def get_book_info(book_name, book_len=None, filename='clippings.txt'):
    """
    returns arrays and lists containing information about the book.
    This information includes all the locations, types of locations, 
    and timestamps for these locations.

    input:
        book_name: the book from which time stamp and location information
                   should be taken
        filename: name of file that has the clipping data (clippings.txt)
        book_len: length of book. Defaults to None and is later assigned the
                  highest location values for the particular book.

    output:
        tuple (list, pylab.array, list):
                arrays and lists containing the timestamps, corresponding 
                percentage complete values, and the location types (N/B/H). 
    """

    assert book_name in get_book_list(filename), "Requested book not found."

    time_stamp_dict = {}
    
    book_file = open(filename, 'r')
    
    while True:
        try:
            book_line = book_file.next().strip()
            if book_line == '==========':
                current_book = re.search('(.*?)\ \(.*?\)', (book_file.next()))
                if current_book.group(1) == book_name:
                    info_ln = book_file.next()
                    info = re.search('- (\w).*? (\d{1,}).*? \| .*?, (.*?)\n', info_ln)
                    loc_type = info.group(1)
                    location = int(info.group(2))
                    time_stamp = time_stamp_formatter(info.group(3))
                    time_stamp_dict[time_stamp] = (location, loc_type)
        except StopIteration:
            break
    
    times = [tm for tm in sorted(time_stamp_dict.keys())]
    locs = [(time_stamp_dict[tm][0]) for tm in sorted(time_stamp_dict.keys())]
    types = [(time_stamp_dict[tm][1]) for tm in sorted(time_stamp_dict.keys())]
    if book_len == None:
        book_len = max(locs)

    locs = pylab.array(locs)/float(book_len)
    
    return times, locs, types

def time_stamp_formatter(raw_stamp):
    """
    converts a raw Kindle time stamp into a datetime object.

    input:
        raw_stamp: time stamp in kindle's format

    output:
        datetime: a datetime object made using the raw_stamp
    """
    
    month_to_num = {"January": 1, "February": 2, "March":3, "April":4, "May":5,
                    "June":6, "July":5, "August":8, "September":9,
                    "October":10, "November":11, "December":12}
    

    kindle_date_format = '(\S+) (\d{1,}), (\d{1,}), (\d{1,}):(\d{1,}) (\S+)'
    formatted_stamp = re.search(kindle_date_format, raw_stamp)

    year = int(formatted_stamp.group(3))
    month = (month_to_num[formatted_stamp.group(1)])
    day = int(formatted_stamp.group(2))
    hour = int(formatted_stamp.group(4))
    minute = int(formatted_stamp.group(5))
    am_pm = formatted_stamp.group(6)

    if (hour == 12) and (am_pm == 'AM'):
        hour = 0
    elif (hour != 12) and am_pm == 'PM':
        hour = hour + 12

    return datetime.datetime(year, month, day, hour, minute)

def plot_book_stats(book_name, book_len=None, filename='clippings.txt'):
    """
    Plots the statistics for the required book. Uses two sub functions to
    carry out minor details of the plotting mechanism.

    inputs:
        book_name: name of the book
        book_len: Length of the book, defaults to None
        filename: clippings filename (defaults to 'clippings.txt')
    """
    
    def plot_progress(times, locs):
        """
        Plots the locations vs. time graph for the book.

        inputs:
            times: pylab array of all the timestamps
            locs: locations (in %) for the corresponding timestamps.

        output:
            None.
        """

        pylab.plot(times, locs, 'b-')
        pylab.plot(times, locs, 'b.')
        pylab.ylim([0, 1])
        pylab.xlabel('Time stamps')
        pylab.ylabel('Location in book (in %')
        pylab.title('Progress with book over time')
        pylab.grid()

    def plot_nbh_dist(locs):
        """
        Plots the frequency of notes, bookmarks and highlights throughout the
        book. The raw locations have been passed through the gaussian_kde()
        method to get the distribution of the required features.

        input:
            locs: locations of all the bookmarks, notes and highlights for the
                  required book (in %)

        output:
            None
        """

        density = gaussian_kde(locs)
        xs = pylab.linspace(0,1,1000)
        density.covariance_factor = lambda : .10
        density._compute_covariance()
        pylab.plot(xs,density(xs), 'r')
        pylab.xlim([0, 1])
        # pylab.xlabel('Book locations (in %)')
        # pylab.ylabel('Freq.')

    def plot_nbh_individual_dist(locs, types):
        """
        Plots individual distributions for notes, bookmarks and highlights.
        Works in a similar fashion as plot_nbh_dist()

        input:
            locs: all the locations with bookmarks, notes, and highlights.
            types: corresponding 'types' of these locations ('B', 'N', 'H')

        output:
            None.
        """

        sep_values = {}
        
        for i in range(len(types)):
            try:
                sep_values[types[i]].append(locs[i])
            except:
                sep_values[types[i]] = [locs[i]]

        densities = []
        colors = {'H':'r', 'B':'g', 'N':'b'}

        for k in sep_values.keys():
            density = gaussian_kde(sep_values[k])
            density.covariance_factor = lambda : .10
            density._compute_covariance()
            xs = pylab.linspace(0,1,1000)
            pylab.plot(xs,density(xs), colors[k], label=k)
        pylab.legend()
        pylab.xlim([0, 1])
        pylab.xlabel('Book locations (in %)')
        # pylab.ylabel('Freq.')

    times, locs, types = get_book_info(book_name, book_len, filename)

    pylab.figure(facecolor='white')
    # pylab.xkcd()

    try:
        pylab.subplot(1, 2, 1)
        plot_progress(times, locs)
    except:
        print 'Error producing plot #1'

    try:
        pylab.subplot(2, 2, 2)
        plot_nbh_dist(locs)
    except:
        print 'Error producing plot #2'

    try:
        pylab.subplot(2, 2, 4)
        plot_nbh_individual_dist(locs, types)
    except:
        print 'Error producing plot #3'

    pylab.show()

if __name__ == '__main__':
    ## Enter your book name here:
    plot_book_stats('BOOK NAME HERE')