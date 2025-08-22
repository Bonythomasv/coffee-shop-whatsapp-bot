import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

logger = logging.getLogger(__name__)

class MultimediaFormatter:
    """
    Create rich multimedia WhatsApp responses with charts, cards, and formatted text.
    """
    
    def __init__(self):
        # Set up matplotlib for clean, modern charts
        plt.style.use('default')
        self.colors = {
            'primary': '#25D366',      # WhatsApp green
            'secondary': '#128C7E',    # Dark green
            'accent': '#34B7F1',       # Light blue
            'warning': '#FF9500',      # Orange
            'success': '#4CAF50',      # Green
            'background': '#F8F9FA',   # Light gray
            'text': '#1F2937',         # Dark gray
            'card_bg': '#FFFFFF'       # White
        }
    
    def create_sales_report_card(self, sales_data: Dict) -> Tuple[str, str]:
        """
        Create a visual sales report card with chart.
        
        Args:
            sales_data: Sales data dictionary
            
        Returns:
            Tuple of (formatted_text, image_url)
        """
        start_time = time.time()
        logger.info("🎨 MULTIMEDIA FORMATTER START - Creating sales report card")
        
        try:
            # Extract data
            items = sales_data.get('best_selling_items', [])[:5]
            if not items:
                return "No sales data available.", None
            
            # Create chart
            chart_start = time.time()
            image_path = self._create_sales_chart(items, chart_type='bar')
            chart_time = (time.time() - chart_start) * 1000
            logger.info(f"⏱️  CHART CREATION TIME: {chart_time:.2f}ms")
            
            # Format text with emojis and rich formatting
            text_start = time.time()
            formatted_text = self._format_sales_report_text(items)
            text_time = (time.time() - text_start) * 1000
            logger.info(f"⏱️  TEXT FORMATTING TIME: {text_time:.2f}ms")
            
            total_time = (time.time() - start_time) * 1000
            logger.info(f"🎨 MULTIMEDIA FORMATTER END - Total time: {total_time:.2f}ms")
            
            return formatted_text, image_path
            
        except Exception as e:
            logger.error(f"Error creating sales report card: {e}")
            return self._fallback_text_format(sales_data), None
    
    def create_weekly_summary_card(self, sales_data: Dict) -> Tuple[str, str]:
        """
        Create a weekly summary card like the example image.
        
        Args:
            sales_data: Sales data dictionary
            
        Returns:
            Tuple of (formatted_text, image_url)
        """
        try:
            items = sales_data.get('best_selling_items', [])
            if not items:
                return "No weekly data available.", None
            
            top_item = items[0]
            
            # Create visual card
            image_path = self._create_weekly_card(top_item)
            
            # Format text message
            formatted_text = f"""📊 *Weekly Report*
            
🏆 *Top Performer*: {top_item['item_name']}
📈 *Sold*: {top_item['quantity_sold']} units
💰 *Revenue*: ${top_item['total_revenue']:.2f}

_Your best-seller is performing great! 🚀_"""
            
            return formatted_text, image_path
            
        except Exception as e:
            logger.error(f"Error creating weekly summary card: {e}")
            return self._fallback_text_format(sales_data), None
    
    def _create_sales_chart(self, items: List[Dict], chart_type: str = 'bar') -> str:
        """Create a sales chart and return the file path."""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor(self.colors['background'])
            
            # Extract data
            names = [item['item_name'][:15] + '...' if len(item['item_name']) > 15 
                    else item['item_name'] for item in items]
            quantities = [item['quantity_sold'] for item in items]
            revenues = [item['total_revenue'] for item in items]
            
            if chart_type == 'bar':
                bars = ax.bar(names, quantities, color=self.colors['primary'], alpha=0.8)
                ax.set_ylabel('Quantity Sold', fontsize=12, color=self.colors['text'])
                ax.set_title('📊 Best Selling Items', fontsize=16, fontweight='bold', 
                           color=self.colors['text'], pad=20)
                
                # Add value labels on bars
                for bar, qty in zip(bars, quantities):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{qty}', ha='center', va='bottom', fontweight='bold')
            
            # Style the chart
            ax.set_facecolor(self.colors['card_bg'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.colors['text'])
            ax.spines['bottom'].set_color(self.colors['text'])
            ax.tick_params(colors=self.colors['text'])
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save chart
            timestamp = int(time.time())
            image_path = f"/tmp/sales_chart_{timestamp}.png"
            plt.savefig(image_path, dpi=150, bbox_inches='tight', 
                       facecolor=self.colors['background'])
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating sales chart: {e}")
            return None
    
    def _create_weekly_card(self, top_item: Dict) -> str:
        """Create a weekly report card similar to the example image."""
        try:
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#2D3748')  # Dark background like the example
            
            # Remove axes
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.axis('off')
            
            # Create main card
            card = FancyBboxPatch((1, 1.5), 8, 3, 
                                boxstyle="round,pad=0.1",
                                facecolor='white',
                                edgecolor='none',
                                alpha=0.95)
            ax.add_patch(card)
            
            # Add chart icon
            chart_icon = FancyBboxPatch((1.5, 3.5), 0.8, 0.6,
                                      boxstyle="round,pad=0.05",
                                      facecolor=self.colors['accent'],
                                      edgecolor='none')
            ax.add_patch(chart_icon)
            
            # Add text content
            ax.text(2.8, 4.2, 'Weekly Report', fontsize=14, fontweight='bold',
                   color=self.colors['warning'], va='center')
            
            ax.text(2.8, 3.7, f"{top_item['item_name']} – {top_item['quantity_sold']} sold",
                   fontsize=16, fontweight='bold', color=self.colors['text'], va='center')
            
            # Add trend indicator (mock +12% growth)
            ax.text(2.8, 3.2, f"📈 +12% vs last week", fontsize=12,
                   color=self.colors['success'], va='center')
            
            # Revenue info
            ax.text(2.8, 2.7, f"Revenue: ${top_item['total_revenue']:.2f}",
                   fontsize=12, color=self.colors['text'], va='center')
            
            plt.tight_layout()
            
            # Save card
            timestamp = int(time.time())
            image_path = f"/tmp/weekly_card_{timestamp}.png"
            plt.savefig(image_path, dpi=150, bbox_inches='tight',
                       facecolor='#2D3748')
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating weekly card: {e}")
            return None
    
    def _format_sales_report_text(self, items: List[Dict]) -> str:
        """Format sales report text with rich WhatsApp formatting."""
        if not items:
            return "No sales data available."
        
        # Limit to top 3 items to keep message shorter
        top_items = items[:3]
        
        # Header with emojis
        text = "📊 *Sales Chart Report*\n\n"
        
        # Top performers section
        text += "🏆 *Top 3 Performers:*\n"
        
        for i, item in enumerate(top_items, 1):
            # Choose emoji based on item type
            emoji = self._get_item_emoji(item['item_name'])
            
            # More compact format
            text += f"{emoji} *{i}. {item['item_name']}* - {item['quantity_sold']} sold, ${item['total_revenue']:.2f}\n"
        
        # Summary statistics
        total_quantity = sum(item['quantity_sold'] for item in items)
        total_revenue = sum(item['total_revenue'] for item in items)
        
        text += f"\n📈 *Total:* {total_quantity} items, ${total_revenue:.2f}\n"
        text += "_Chart created! 📊_"
        
        # Ensure message is under WhatsApp's 4096 character limit
        if len(text) > 1000:  # Conservative limit
            # Fallback to even shorter format
            text = f"📊 *Sales Chart*\n\n🏆 Top item: *{top_items[0]['item_name']}* ({top_items[0]['quantity_sold']} sold)\n📈 Total: {total_quantity} items, ${total_revenue:.2f}"
        
        return text
    
    def _get_item_emoji(self, item_name: str) -> str:
        """Get appropriate emoji for item type."""
        item_lower = item_name.lower()
        
        if any(word in item_lower for word in ['coffee', 'latte', 'cappuccino', 'espresso']):
            return "☕"
        elif any(word in item_lower for word in ['scone', 'muffin', 'croissant', 'pastry']):
            return "🥐"
        elif any(word in item_lower for word in ['sandwich', 'focaccia', 'bagel']):
            return "🥪"
        elif any(word in item_lower for word in ['cookie', 'cake', 'brownie']):
            return "🍪"
        elif any(word in item_lower for word in ['tea', 'chai']):
            return "🍵"
        elif any(word in item_lower for word in ['smoothie', 'juice']):
            return "🥤"
        else:
            return "🍽️"
    
    def _fallback_text_format(self, sales_data: Dict) -> str:
        """Fallback text formatting if multimedia creation fails."""
        items = sales_data.get('best_selling_items', [])
        if not items:
            return "No sales data available."
        
        text = "📊 *Sales Report*\n\n"
        for i, item in enumerate(items[:5], 1):
            emoji = self._get_item_emoji(item['item_name'])
            text += f"{emoji} {i}. *{item['item_name']}*\n"
            text += f"   Sold: {item['quantity_sold']} | ${item['total_revenue']:.2f}\n\n"
        
        return text
    
    def create_comparison_chart(self, current_data: List[Dict], 
                              previous_data: List[Dict] = None) -> Tuple[str, str]:
        """
        Create a comparison chart showing current vs previous period.
        
        Args:
            current_data: Current period sales data
            previous_data: Previous period sales data (optional)
            
        Returns:
            Tuple of (formatted_text, image_url)
        """
        try:
            if not previous_data:
                # If no previous data, create simple current period chart
                return self.create_sales_report_card({'best_selling_items': current_data})
            
            # Create comparison chart
            image_path = self._create_comparison_chart(current_data, previous_data)
            
            # Format comparison text
            formatted_text = self._format_comparison_text(current_data, previous_data)
            
            return formatted_text, image_path
            
        except Exception as e:
            logger.error(f"Error creating comparison chart: {e}")
            return self._fallback_text_format({'best_selling_items': current_data}), None
    
    def _create_comparison_chart(self, current: List[Dict], previous: List[Dict]) -> str:
        """Create a side-by-side comparison chart."""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            fig.patch.set_facecolor(self.colors['background'])
            
            # Current period
            current_names = [item['item_name'][:10] for item in current[:5]]
            current_qty = [item['quantity_sold'] for item in current[:5]]
            
            ax1.bar(current_names, current_qty, color=self.colors['primary'], alpha=0.8)
            ax1.set_title('📊 Current Period', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Quantity Sold')
            
            # Previous period
            previous_names = [item['item_name'][:10] for item in previous[:5]]
            previous_qty = [item['quantity_sold'] for item in previous[:5]]
            
            ax2.bar(previous_names, previous_qty, color=self.colors['secondary'], alpha=0.8)
            ax2.set_title('📈 Previous Period', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Quantity Sold')
            
            # Style both charts
            for ax in [ax1, ax2]:
                ax.set_facecolor(self.colors['card_bg'])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = int(time.time())
            image_path = f"/tmp/comparison_chart_{timestamp}.png"
            plt.savefig(image_path, dpi=150, bbox_inches='tight',
                       facecolor=self.colors['background'])
            plt.close()
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating comparison chart: {e}")
            return None
    
    def _format_comparison_text(self, current: List[Dict], previous: List[Dict]) -> str:
        """Format comparison text with growth indicators."""
        text = "📊 *Period Comparison Report*\n\n"
        
        # Calculate totals
        current_total = sum(item['quantity_sold'] for item in current)
        previous_total = sum(item['quantity_sold'] for item in previous)
        
        if previous_total > 0:
            growth = ((current_total - previous_total) / previous_total) * 100
            growth_emoji = "📈" if growth > 0 else "📉" if growth < 0 else "➡️"
            text += f"{growth_emoji} *Overall Growth: {growth:+.1f}%*\n\n"
        
        text += "🏆 *Top Performers This Period:*\n"
        for i, item in enumerate(current[:3], 1):
            emoji = self._get_item_emoji(item['item_name'])
            text += f"{emoji} {i}. *{item['item_name']}*: {item['quantity_sold']} sold\n"
        
        return text
