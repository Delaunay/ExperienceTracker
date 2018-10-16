Experience Tracker
==================

WIP/POC

Provide an interface to save experiment.

* The system spec where the experiment is saved
* The experiment (script hash, commit hash, arguments) are saved
* The experiment results (stdout, stderr) are saved by default

Additionally users can use `experiment_tracker.logger` to save specific metric.
The `logger` provide a simple key value store and a stat stream that allows you get the averages and standard deviation
of quantitative metrics.

All the data is saved locally in a json database. The database can be inspected using the explorer script that is going to 
start a small local webserver.

Ultimately, we would like the local database to be uploadable to a Json database.


# CLI Usage

    # Launch an experiement we want to keep track of
    > exp-tracker -- main.py. -b 256 -j 4 -a resnet50 --data /data/img_net --gpu --half
   

    # Consult or compare experiement
    > exp-explorer benchmark.db
    
# Package Usage

    from experience_tracker.logger import TrackLogger
   
    tracker = TrackLogger()
    model_metric = tracker.namespace('model_metric')
    perf_metric = tracker.namespace('perf_metric')
    
    for epoch in range(0, 100):
    
        for (x, y) in dataset:
            
            start = time()
            out = model(x)
            cost(out, y)
            
            optmize()
            end = time()
            
            # will compute averages & sd of those values
            perf_metric.push_stream('data_load_time', load_time)
            perf_metric.push_stream('bash_time', end - start)
            
            model_metric.push_stream('loss_improvement', loss_2 - loss_1)
            
         model_metric.push('accuracy_E{}'.format(epoch), acc)
    
    
    model_metric.push('accucary_final', acc)
    