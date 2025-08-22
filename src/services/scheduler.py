import logging
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.services.sales_processor import SalesProcessor
from src.models.user import db
from src.config import Config

logger = logging.getLogger(__name__)

class SalesDataScheduler:
    """
    Background scheduler for automatic sales data refresh.
    """
    
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.sales_processor = None
        
    def init_app(self, app):
        """Initialize scheduler with Flask app context."""
        self.app = app
        with app.app_context():
            self.sales_processor = SalesProcessor()
        
    def start(self):
        """Start the background scheduler."""
        if not self.scheduler.running:
            # Schedule daily sales data refresh at 11:55 PM
            self.scheduler.add_job(
                func=self._refresh_sales_data,
                trigger=CronTrigger(hour=23, minute=55),  # 11:55 PM
                id='daily_sales_refresh',
                name='Daily Sales Data Refresh',
                replace_existing=True
            )
            
            # Add a startup job to refresh data if cache is stale
            self.scheduler.add_job(
                func=self._startup_refresh_check,
                trigger='date',
                run_date=datetime.now() + timedelta(seconds=30),  # Run 30 seconds after startup
                id='startup_refresh_check',
                name='Startup Cache Check'
            )
            
            self.scheduler.start()
            logger.info("📅 Sales data scheduler started - Daily refresh at 11:55 PM")
        
    def stop(self):
        """Stop the background scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("📅 Sales data scheduler stopped")
    
    def _refresh_sales_data(self):
        """
        Refresh sales data for all merchants.
        This runs in the background scheduler context.
        """
        start_time = time.time()
        logger.info("🔄 SCHEDULED REFRESH START - Daily sales data refresh at 11:55 PM")
        
        try:
            with self.app.app_context():
                # Get merchant ID from config
                merchant_id = Config.CLOVER_MERCHANT_ID
                
                if not merchant_id:
                    logger.warning("⚠️  No merchant ID configured - skipping scheduled refresh")
                    return
                
                # Process and cache sales data
                refresh_start = time.time()
                success = self.sales_processor.process_and_cache_sales_data(merchant_id)
                refresh_time = (time.time() - refresh_start) * 1000
                
                if success:
                    total_time = (time.time() - start_time) * 1000
                    logger.info(f"✅ SCHEDULED REFRESH SUCCESS - Merchant: {merchant_id}, "
                              f"Refresh time: {refresh_time:.2f}ms, Total time: {total_time:.2f}ms")
                else:
                    logger.error(f"❌ SCHEDULED REFRESH FAILED - Merchant: {merchant_id}")
                    
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            logger.error(f"❌ SCHEDULED REFRESH ERROR - Time: {total_time:.2f}ms, Error: {e}")
    
    def _startup_refresh_check(self):
        """
        Check if cache is stale on startup and refresh if needed.
        """
        start_time = time.time()
        logger.info("🚀 STARTUP REFRESH CHECK - Checking cache freshness")
        
        try:
            with self.app.app_context():
                merchant_id = Config.CLOVER_MERCHANT_ID
                
                if not merchant_id:
                    logger.info("⚠️  No merchant ID configured - skipping startup refresh check")
                    return
                
                # Check if cache is fresh (within 24 hours)
                cache_hours = Config.CACHE_EXPIRY_HOURS or 24
                is_fresh = self.sales_processor.is_cache_fresh(merchant_id, cache_hours)
                
                if not is_fresh:
                    logger.info(f"🔄 Cache is stale - refreshing sales data for merchant: {merchant_id}")
                    refresh_start = time.time()
                    success = self.sales_processor.process_and_cache_sales_data(merchant_id)
                    refresh_time = (time.time() - refresh_start) * 1000
                    
                    if success:
                        total_time = (time.time() - start_time) * 1000
                        logger.info(f"✅ STARTUP REFRESH SUCCESS - Refresh time: {refresh_time:.2f}ms, "
                                  f"Total time: {total_time:.2f}ms")
                    else:
                        logger.error("❌ STARTUP REFRESH FAILED")
                else:
                    total_time = (time.time() - start_time) * 1000
                    logger.info(f"✅ STARTUP REFRESH CHECK - Cache is fresh, no refresh needed. "
                              f"Check time: {total_time:.2f}ms")
                    
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            logger.error(f"❌ STARTUP REFRESH CHECK ERROR - Time: {total_time:.2f}ms, Error: {e}")
    
    def get_next_refresh_time(self):
        """Get the next scheduled refresh time."""
        job = self.scheduler.get_job('daily_sales_refresh')
        if job:
            return job.next_run_time
        return None
    
    def trigger_manual_refresh(self):
        """Trigger a manual refresh immediately."""
        logger.info("🔄 MANUAL REFRESH TRIGGERED")
        self._refresh_sales_data()
    
    def get_scheduler_status(self):
        """Get scheduler status and job information."""
        return {
            'running': self.scheduler.running,
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
                for job in self.scheduler.get_jobs()
            ]
        }
