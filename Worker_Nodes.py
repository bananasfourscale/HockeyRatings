from multiprocessing import Queue
#from Plotter import plot_data_set, plot_trend_set, plot_player_ranking

def plotter_worker(input_queue : Queue=None, id : int=0):
    i = 0
    for func, arg_list in iter(input_queue.get, 'STOP'):
        func(*arg_list)
        print("worker {} completed graph {}".format(id, i))
        i += 1
    print("Exiting! this worker {} ran {} plots".format(id, i))
