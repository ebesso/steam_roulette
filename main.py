from init_app import create_app, socketio
from handlers import roulette, trade_offers, configuration

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import atexit, os

scheduler = BackgroundScheduler()

app = create_app(True)

@app.before_first_request
def before_first_request():
    roulette.init_roulette()

    scheduler.add_job(
        func=roulette.time_roulettes,
        trigger='interval',
        seconds=1
    )

    scheduler.add_job(
        func=trade_offers.check_trade_offers,
        trigger='interval',
        seconds=int(configuration.get('trade_offers').trade_offer_poll_interval)
    )

    scheduler.start()

atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))        
    socketio.run(app, host='0.0.0.0' , port=port)