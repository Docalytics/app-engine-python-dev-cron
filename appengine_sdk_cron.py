import threading, thread, yaml, os, argparse, sys, time, urllib2
from datetime import datetime

APP_ENGINE_APP_URL = None   #(String) path to your Google Appengine app folder (where your cron.yaml file lives)
LOGGING_ENABLED = None      #(True|False) is logging enabled for this script

#main function to load/run all the defined cron jobs for the app located at 'app_path'
def run_cron_scheduler( app_path ):
    #grab the cron definitions from the yaml file
    cron_jobs = _load_cron_yaml( app_path )
    if not cron_jobs:
        raise RuntimeError("Appegine_SDK_Cron: No cronjobs found to run for the app at '"+app_path+"'")
        return
    else:
        print "=== STARTING SCHEDULED EXECUTION OF "+str(len(cron_jobs))+" CRON JOBS ==="
    #iterate through each job and start a new thread for each, which waits until it's time to run the job, then
    #runs it (in a separate thread), then the thread gets the next time to run and waits, etc etc
    for key in range(len(cron_jobs)):
        job = cron_jobs[key]
        schedule = job.get('schedule')
        timezone = job.get('timezone')
        time_schedule = groctimespecification.GrocTimeSpecification( schedule, timezone )
        cron_jobs[key]['time_schedule'] = time_schedule
        cron_jobs[key]['num_times_ran'] = 0
        #create the new child thread to control this job, define it as a daemon thread, and start it up
        child_thread = threading.Thread( target=run_individual_job_thread, args=(cron_jobs[key],) )
        child_thread.daemon = True
        child_thread.start()
    #keep the parent thread alive
    while threading.active_count() > 0:
        time.sleep(0.1)

#control thread for a specific job - determine when a job is supposed to run (from current time), then create a new thread
#whic waits that long to execute, then fire up the job. Rinse, repeat...
def run_individual_job_thread( job ):
    while True:
        cur_time = datetime.now()
        next_iteration_run = job['time_schedule'].GetMatch( cur_time )
        run_in_seconds = (next_iteration_run-cur_time).seconds
        if LOGGING_ENABLED:
            print "::JOB AT "+job['url']+' SCHEDULED TO RUN AT '+next_iteration_run.strftime('%c')+' (in '+str(run_in_seconds)+' seconds)'
        #wait the appropriate # of seconds before running the job w/ a new thread, then block until the job is started and the thread returns
        timer_thread = threading.Timer( float(run_in_seconds), execute_cron_job_thread, (job,) )
        timer_thread.daemon=True
        timer_thread.start()
        timer_thread.join()

#function called from individual job control timed thread to actually execute the job itself
#NOTE: this function is non-blocking for the parent thread, as all it needs to do is simply start the job and return
#since the job is started as a new thread, this function should return extremely fast so the timer statys in sync
def execute_cron_job_thread( job ):
    thread.start_new_thread( execute_cron_job, (job,) )
    job['num_times_ran'] += 1

#This function executes the actual individual cronjob - i.e. calls the specified URL in the app
def execute_cron_job( job ):
    success = True
    try:
        resp = urllib2.urlopen( APP_ENGINE_APP_URL+job.get('url') , timeout=9999 )
        if resp.code != 200:
            #cron job URL returned a 200 status - assume it executed successfully
            success = False
    except:
        success = False
    if LOGGING_ENABLED:
        print ':'+ datetime.now().strftime('[%I:%M%p]')+" Job '"+APP_ENGINE_APP_URL+job.get('url')+"' executed ("+("Success" if success else "Failed" )+")"
    return

#This function loads the cron yaml file from the supplied app directory (if it exists)
def _load_cron_yaml( app_path ):
    yaml_file = app_path+'/cron.yaml'
    if not os.path.exists( yaml_file ):
        raise RuntimeError("Appegine_SDK_Cron: Unable to location cron.yaml file in directory.")
    stream = open( os.path.join(os.path.abspath(os.path.dirname(yaml_file)), 'cron.yaml'), 'r')
    yaml_cont = yaml.load(stream)
    return None if 'cron' not in yaml_cont or len(yaml_cont['cron']) == 0 else yaml_cont['cron']


if __name__ == '__main__':
    #description of this script
    parser = argparse.ArgumentParser(description="Appengine SDK Cron Scheduler")

    #--app_path argument is the FULL file path to your GAE root application folder (where cron.yaml file is)
    parser.add_argument('-ap', '--app_path',
                        help="The file path to your application",
                        required=True,
                        action="store")

    #--appengine_path argument is the full file path to your root GAE install directory
    parser.add_argument('-gae', '--gae_path',
                        help="The path to your google app engine SDK direcotry",
                        required=True,
                        action="store"
    )

    #--app_url argument is the full URL path to your running SDK app instance (including scheme/port - ex http://localhost:8080)
    parser.add_argument('-au', '--app_url',
                        help="The full url path (including scheme/port) to your running application",
                        default='http://localhost:8080',
                        action="store"
    )

    #--disable_logging flag, when included, disables logging for the script
    parser.add_argument('-dl', '--disable_logging',
                        help="Do you wish logging enabled",
                        default=False,
                        action="store_false"
    )

    #grab the needed results from the arg parser, set the needed vars in the module, and run the cron job scheduler
    results = parser.parse_args()
    sys.path.append(results.gae_path)
    LOGGING_ENABLED = False if results.disable_logging else True
    APP_ENGINE_APP_URL = results.app_url
    from google.appengine.cron import groctimespecification
    run_cron_scheduler( results.app_path )