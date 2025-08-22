"""
LLM client for generating natural language responses using various LLM providers.
Supported providers: OpenAI, DeepSeek, Together AI, xAI
"""

import logging
import openai
from typing import Dict, List, Optional, Union
from src.config import Config

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with LLM services."""
    
    def __init__(self):
        """Initialize the LLM client with the configured provider."""
        self.provider = Config.LLM_PROVIDER
        self.client = None
        self.model = None
        self.use_llm = False
        
        # Initialize the appropriate client based on provider
        if self.provider == 'openai' and Config.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.OPENAI_MODEL
            self.use_llm = True
            logger.info(f"Using OpenAI with model: {self.model}")
            
        elif self.provider == 'deepseek' and Config.DEEPSEEK_API_KEY:
            self.client = openai.OpenAI(
                api_key=Config.DEEPSEEK_API_KEY,
                base_url=Config.DEEPSEEK_API_BASE
            )
            self.model = Config.DEEPSEEK_MODEL
            self.use_llm = True
            logger.info(f"Using DeepSeek with model: {self.model}")
            
        elif self.provider == 'together' and Config.TOGETHER_API_KEY:
            self.client = openai.OpenAI(
                api_key=Config.TOGETHER_API_KEY,
                base_url="https://api.together.xyz/v1"
            )
            self.model = Config.TOGETHER_MODEL
            self.use_llm = True
            logger.info(f"Using Together AI with model: {self.model}")
            
        elif self.provider == 'xai' and Config.XAI_API_KEY:
            # xAI would require custom client implementation
            logger.warning("xAI provider is not fully implemented yet, using fallback")
            
        if not self.use_llm:
            logger.warning(f"LLM provider '{self.provider}' not properly configured, using fallback responses")
    
    def generate_response(self, question: str, context: str = "", sales_data: Dict = None) -> str:
        """
        Generate a response using the configured LLM provider.
        
        Args:
            question: The user's question
            context: Additional context for the LLM
            sales_data: Sales data to include in the response
            
        Returns:
            Generated response text
        """
        try:
            if self.use_llm and self.client:
                return self._generate_llm_response(question, context, sales_data)
            else:
                return self._generate_fallback_response(question, sales_data)
                
        except Exception as e:
            logger.error(f"Error generating {self.provider} response: {e}")
            return self._generate_fallback_response(question, sales_data)
    
    def _generate_llm_response(self, question: str, context: str, sales_data: Dict = None) -> str:
        """Generate response using the configured LLM provider."""
        if not self.use_llm or not self.client:
            return self._generate_fallback_response(question, sales_data)
            
        try:
            # Prepare the prompt
            prompt = self._prepare_prompt(question, context, sales_data)
            
            # Common parameters for all providers
            params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant for a coffee shop owner. You provide clear, concise, and friendly responses about sales data and business analytics. Always be professional but approachable."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.7
            }
            
            # Provider-specific adjustments
            if self.provider == 'deepseek':
                # DeepSeek specific parameters if needed
                pass
            elif self.provider == 'together':
                # Together AI specific parameters
                params['stop'] = ['</s>', '###']
            
            # Make API call to the configured provider
            response = self.client.chat.completions.create(**params)
            
            # Extract the response
            generated_text = response.choices[0].message.content.strip()
            
            # Validate response length
            if len(generated_text) < 10:
                logger.warning(f"{self.provider.capitalize()} response too short, using fallback")
                return self._generate_fallback_response(question, sales_data)
            
            return generated_text
            
        except Exception as e:
            logger.error(f"{self.provider.capitalize()} API error: {e}")
            return self._generate_fallback_response(question, sales_data)
    
    def _prepare_prompt(self, question: str, context: str, sales_data: Dict = None) -> str:
        """Prepare the prompt for the LLM."""
        prompt_parts = []
        
        # Add context if provided
        if context:
            prompt_parts.append(f"Context: {context}")
        
        # Add sales data if provided
        if sales_data and sales_data.get('best_selling_items'):
            prompt_parts.append("Current sales data:")
            
            items = sales_data['best_selling_items'][:5]  # Top 5 items
            for i, item in enumerate(items, 1):
                prompt_parts.append(
                    f"{i}. {item['item_name']}: {item['quantity_sold']} sold, "
                    f"${item['total_revenue']:.2f} revenue"
                )
            
            if sales_data.get('category_filter'):
                prompt_parts.append(f"(Filtered by category: {sales_data['category_filter']})")
        
        # Add the user's question
        prompt_parts.append(f"Question: {question}")
        
        # Add instructions
        prompt_parts.append(
            "Please provide a helpful, friendly response based on the sales data above. "
            "Keep it concise and business-focused. If asking about best-selling items, "
            "mention specific numbers and revenue when available."
        )
        
        return "\\n\\n".join(prompt_parts)
    
    def _generate_fallback_response(self, question: str, sales_data: Dict = None) -> str:
        """Generate a fallback response without LLM."""
        question_lower = question.lower()
        
        # Handle best-selling questions
        if "best" in question_lower and ("selling" in question_lower or "popular" in question_lower):
            if sales_data and sales_data.get('best_selling_items'):
                items = sales_data['best_selling_items']
                if items:
                    top_item = items[0]
                    response = f"Your best-selling item is {top_item['item_name']} with {top_item['quantity_sold']} units sold"
                    
                    if len(items) > 1:
                        response += f", followed by {items[1]['item_name']} with {items[1]['quantity_sold']} units"
                    
                    response += f". Total revenue from {top_item['item_name']}: ${top_item['total_revenue']:.2f}."
                    return response
            
            return "Based on your recent sales data, Cappuccino appears to be your best-selling item this week."
        
        # Handle greeting messages
        elif any(word in question_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm your coffee shop sales assistant. I can help you analyze your sales data and answer questions about your business performance."
        
        # Handle help requests
        elif "help" in question_lower:
            return self._get_help_message()
        
        # Handle coffee/drink specific questions
        elif any(word in question_lower for word in ["coffee", "drink", "beverage"]):
            if sales_data and sales_data.get('best_selling_items'):
                coffee_items = [item for item in sales_data['best_selling_items'] 
                              if item.get('category') == 'Coffee']
                if coffee_items:
                    top_coffee = coffee_items[0]
                    return f"Your top coffee drink is {top_coffee['item_name']} with {top_coffee['quantity_sold']} sold and ${top_coffee['total_revenue']:.2f} in revenue."
            
            return "Your coffee sales are performing well. Cappuccino and Latte are typically your top performers."
        
        # Handle sales/revenue questions
        elif any(word in question_lower for word in ["sales", "revenue", "income", "money"]):
            if sales_data and sales_data.get('best_selling_items'):
                total_revenue = sum(item['total_revenue'] for item in sales_data['best_selling_items'])
                total_items = sum(item['quantity_sold'] for item in sales_data['best_selling_items'])
                return f"Your recent sales show {total_items} items sold with ${total_revenue:.2f} in total revenue from your top items."
            
            return "Your sales data shows consistent performance across your menu items."
        
        # Default response
        else:
            return "I understand you're asking about your business data. Let me help you with that information based on your recent sales. Try asking about your best-selling items or specific product performance."
    
    def _get_help_message(self) -> str:
        """Get help message with available commands."""
        return """I can help you with your coffee shop sales data! Here are some things you can ask:

• "What's my best-selling drink this week?"
• "How many cappuccinos did I sell?"
• "What are my top 5 items?"
• "Show me coffee sales"
• "What's my revenue today?"

Just ask me any question about your sales and I'll help you find the answer!"""
    
    def analyze_sales_trends(self, sales_data: List[Dict], question: str) -> str:
        """
        Analyze sales trends and provide insights using the configured LLM provider.
        
        Args:
            sales_data: List of sales data dictionaries
            question: User's question about trends
            
        Returns:
            Analysis response
        """
        if not sales_data:
            return "I don't have enough sales data to analyze trends right now."
        
        if not self.use_llm or not self.client:
            return self._simple_trend_analysis(sales_data, question)
        
        try:
            # Prepare trend analysis prompt
            prompt = f"""
            Analyze the following sales data and answer the question: {question}
            
            Sales Data:
            {self._format_sales_data_for_analysis(sales_data)}
            
            Please provide insights about trends, patterns, or specific answers to the question.
            Keep the response concise and actionable for a coffee shop owner.
            """
            
            # Common parameters for all providers
            params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a business analyst specializing in coffee shop operations. Provide clear, actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.5
            }
            
            # Provider-specific adjustments
            if self.provider == 'deepseek':
                # DeepSeek specific parameters if needed
                pass
            elif self.provider == 'together':
                # Together AI specific parameters
                params['stop'] = ['</s>', '###']
            
            # Make API call to the configured provider
            response = self.client.chat.completions.create(**params)
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in {self.provider} trend analysis: {e}")
            return self._simple_trend_analysis(sales_data, question)
    
    def _format_sales_data_for_analysis(self, sales_data: List[Dict]) -> str:
        """Format sales data for LLM analysis."""
        formatted_lines = []
        for item in sales_data[:10]:  # Limit to top 10 items
            formatted_lines.append(
                f"- {item['item_name']}: {item['quantity_sold']} sold, "
                f"${item['total_revenue']:.2f} revenue, Category: {item.get('category', 'Unknown')}"
            )
        return "\\n".join(formatted_lines)
    
    def _simple_trend_analysis(self, sales_data: List[Dict], question: str) -> str:
        """Simple trend analysis without LLM."""
        if not sales_data:
            return "No sales data available for analysis."
        
        # Basic analysis
        total_items = sum(item['quantity_sold'] for item in sales_data)
        total_revenue = sum(item['total_revenue'] for item in sales_data)
        avg_price = total_revenue / total_items if total_items > 0 else 0
        
        # Category breakdown
        categories = {}
        for item in sales_data:
            category = item.get('category', 'Unknown')
            if category not in categories:
                categories[category] = {'items': 0, 'revenue': 0}
            categories[category]['items'] += item['quantity_sold']
            categories[category]['revenue'] += item['total_revenue']
        
        top_category = max(categories.items(), key=lambda x: x[1]['items'])[0] if categories else "Unknown"
        
        return f"""Sales Analysis:
• Total items sold: {total_items}
• Total revenue: ${total_revenue:.2f}
• Average price per item: ${avg_price:.2f}
• Top category: {top_category}
• Best performer: {sales_data[0]['item_name']} ({sales_data[0]['quantity_sold']} sold)"""

