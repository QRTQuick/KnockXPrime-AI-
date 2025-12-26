#!/usr/bin/env python3
"""
KnockXPrime AI - CLI Frontend
A beautiful command-line interface for the KnockXPrime AI service
"""
import asyncio
import httpx
import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# Third-party imports
import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
import click

# Initialize Rich console
console = Console()

class KnockXPrimeClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_key = None
        self.user_data = None
        self.session_file = os.path.expanduser("~/.knockxprime_session")
    
    def load_session(self):
        """Load saved session data"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    self.api_key = data.get('api_key')
                    self.user_data = data.get('user_data')
                    return True
        except Exception:
            pass
        return False
    
    def save_session(self):
        """Save session data"""
        try:
            data = {
                'api_key': self.api_key,
                'user_data': self.user_data
            }
            with open(self.session_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass
    
    def clear_session(self):
        """Clear saved session"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception:
            pass
        self.api_key = None
        self.user_data = None
    
    async def health_check(self) -> bool:
        """Check if API is available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health/", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False
    
    async def register(self, username: str, email: str, password: str, plan: str = "Leveler") -> Dict[str, Any]:
        """Register a new user"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/users/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "plan_name": plan
                }
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/users/login",
                json={"username": username, "password": password}
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile"""
        if not self.api_key:
            return {"status_code": 401, "data": {"detail": "Not authenticated"}}
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/users/profile",
                headers=headers
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def get_plans(self) -> Dict[str, Any]:
        """Get available plans"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/v1/plans/")
            return {"status_code": response.status_code, "data": response.json()}
    
    async def chat_completion(self, messages: list, max_tokens: int = 1000) -> Dict[str, Any]:
        """Send chat completion request"""
        if not self.api_key:
            return {"status_code": 401, "data": {"detail": "Not authenticated"}}
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/chat/completions",
                headers=headers,
                json={
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=60.0
            )
            return {"status_code": response.status_code, "data": response.json()}
    
    async def get_usage(self) -> Dict[str, Any]:
        """Get usage statistics"""
        if not self.api_key:
            return {"status_code": 401, "data": {"detail": "Not authenticated"}}
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/usage/current",
                headers=headers
            )
            return {"status_code": response.status_code, "data": response.json()}


class KnockXPrimeCLI:
    def __init__(self):
        self.client = KnockXPrimeClient()
        self.conversation_history = []
    
    def display_banner(self):
        """Display the application banner"""
        # Create ASCII art title
        title = pyfiglet.figlet_format("KnockXPrime", font="slant")
        subtitle = pyfiglet.figlet_format("AI", font="big")
        
        # Create colorful banner
        banner_text = Text()
        banner_text.append(title, style="bold cyan")
        banner_text.append(subtitle, style="bold magenta")
        
        panel = Panel(
            banner_text,
            title="🚀 Welcome to KnockXPrime AI",
            subtitle="Your Premium AI Assistant",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    def display_menu(self):
        """Display main menu"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="bold cyan", width=4)
        menu_table.add_column("Description", style="white")
        
        if self.client.api_key:
            menu_table.add_row("1.", "💬 Start Chat Session")
            menu_table.add_row("2.", "📊 View Usage Statistics")
            menu_table.add_row("3.", "👤 View Profile")
            menu_table.add_row("4.", "💳 View Plans")
            menu_table.add_row("5.", "🚪 Logout")
            menu_table.add_row("6.", "❌ Exit")
        else:
            menu_table.add_row("1.", "🔐 Login")
            menu_table.add_row("2.", "📝 Register")
            menu_table.add_row("3.", "💳 View Plans")
            menu_table.add_row("4.", "🔧 Settings")
            menu_table.add_row("5.", "❌ Exit")
        
        panel = Panel(
            menu_table,
            title="🎯 Main Menu",
            border_style="green",
            padding=(1, 1)
        )
        
        console.print(panel)
    
    async def check_connection(self):
        """Check API connection with loading animation"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("🔍 Checking API connection...", total=None)
            
            is_connected = await self.client.health_check()
            
            if is_connected:
                console.print("✅ [green]Connected to KnockXPrime AI API[/green]")
                return True
            else:
                console.print("❌ [red]Failed to connect to API. Please check if the server is running.[/red]")
                return False
    
    async def login_flow(self):
        """Handle user login"""
        console.print("\n[bold cyan]🔐 Login to KnockXPrime AI[/bold cyan]")
        console.print()
        
        username = Prompt.ask("👤 Username")
        password = Prompt.ask("🔒 Password", password=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("🔄 Authenticating...", total=None)
            
            result = await self.client.login(username, password)
        
        if result["status_code"] == 200:
            data = result["data"]
            self.client.user_data = data["user"]
            
            # Get API key from profile
            profile_result = await self.client.get_profile()
            if profile_result["status_code"] == 200:
                self.client.api_key = profile_result["data"]["api_key"]
                self.client.save_session()
                
                console.print(f"✅ [green]Welcome back, {self.client.user_data['username']}![/green]")
                console.print(f"📋 Plan: [cyan]{self.client.user_data['plan_name']}[/cyan]")
                return True
        
        console.print("❌ [red]Login failed. Please check your credentials.[/red]")
        return False
    
    async def register_flow(self):
        """Handle user registration"""
        console.print("\n[bold cyan]📝 Register for KnockXPrime AI[/bold cyan]")
        console.print()
        
        # Show available plans first
        await self.show_plans()
        console.print()
        
        username = Prompt.ask("👤 Username")
        email = Prompt.ask("📧 Email")
        password = Prompt.ask("🔒 Password", password=True)
        plan = Prompt.ask("💳 Plan", choices=["Baby Free", "Leveler", "Log Min", "High Max"], default="Baby Free")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("📝 Creating account...", total=None)
            
            result = await self.client.register(username, email, password, plan)
        
        if result["status_code"] == 200:
            console.print("✅ [green]Account created successfully![/green]")
            console.print("🔐 [yellow]Please login with your credentials.[/yellow]")
            return True
        else:
            error_msg = result["data"].get("detail", "Registration failed")
            console.print(f"❌ [red]{error_msg}[/red]")
            return False
    
    async def show_plans(self):
        """Display available subscription plans"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("📋 Loading plans...", total=None)
            
            result = await self.client.get_plans()
        
        if result["status_code"] == 200:
            plans = result["data"]
            
            plans_table = Table(title="💳 Subscription Plans", show_header=True, header_style="bold magenta")
            plans_table.add_column("Plan", style="cyan", width=12)
            plans_table.add_column("Price", style="green", width=10)
            plans_table.add_column("Tokens/Day", style="yellow", width=12)
            plans_table.add_column("Requests/Day", style="blue", width=14)
            plans_table.add_column("Value", style="white", width=10)
            
            for plan in plans:
                if plan['price'] > 0:
                    value_per_dollar = plan['max_tokens'] / plan['price']
                    value_display = f"{value_per_dollar:.0f}/$ "
                else:
                    value_display = "Free"
                
                plans_table.add_row(
                    plan['name'],
                    f"${plan['price']:.2f}" if plan['price'] > 0 else "Free",
                    f"{plan['max_tokens']:,}",
                    f"{plan.get('max_requests', 'N/A'):,}" if isinstance(plan.get('max_requests'), int) else "N/A",
                    value_display
                )
            
            console.print(plans_table)
        else:
            console.print("❌ [red]Failed to load plans[/red]")
    
    async def show_profile(self):
        """Display user profile"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("👤 Loading profile...", total=None)
            
            result = await self.client.get_profile()
        
        if result["status_code"] == 200:
            profile = result["data"]
            
            profile_table = Table(show_header=False, box=None, padding=(0, 2))
            profile_table.add_column("Field", style="bold cyan", width=15)
            profile_table.add_column("Value", style="white")
            
            profile_table.add_row("Username:", profile['username'])
            profile_table.add_row("Email:", profile['email'])
            profile_table.add_row("Plan:", f"[green]{profile['plan_name']}[/green]")
            profile_table.add_row("Max Tokens:", f"{profile['max_tokens']:,}")
            profile_table.add_row("Monthly Price:", f"[green]${profile['price']:.2f}[/green]")
            profile_table.add_row("API Key:", f"{profile['api_key'][:20]}...")
            profile_table.add_row("Member Since:", profile['created_at'][:10])
            
            panel = Panel(
                profile_table,
                title="👤 Your Profile",
                border_style="cyan",
                padding=(1, 1)
            )
            
            console.print(panel)
        else:
            console.print("❌ [red]Failed to load profile[/red]")
    
    async def show_usage(self):
        """Display usage statistics"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("📊 Loading usage stats...", total=None)
            
            result = await self.client.get_usage()
        
        if result["status_code"] == 200:
            usage = result["data"]
            
            # Calculate usage percentage
            usage_percent = (usage['tokens_used'] / usage['max_tokens']) * 100
            
            usage_table = Table(show_header=False, box=None, padding=(0, 2))
            usage_table.add_column("Metric", style="bold cyan", width=20)
            usage_table.add_column("Value", style="white")
            
            usage_table.add_row("Plan:", f"[green]{usage['plan_name']}[/green]")
            usage_table.add_row("Tokens Used Today:", f"{usage['tokens_used']:,}")
            usage_table.add_row("Tokens Remaining:", f"[yellow]{usage['tokens_remaining']:,}[/yellow]")
            usage_table.add_row("Daily Token Limit:", f"{usage['max_tokens']:,}")
            usage_table.add_row("Requests Made Today:", f"{usage['requests_made']:,}")
            usage_table.add_row("Requests Remaining:", f"[yellow]{usage['requests_remaining']:,}[/yellow]")
            usage_table.add_row("Daily Request Limit:", f"{usage['max_requests']:,}")
            usage_table.add_row("Usage Percentage:", f"[{'red' if usage_percent > 80 else 'yellow' if usage_percent > 50 else 'green'}]{usage_percent:.1f}%[/]")
            
            panel = Panel(
                usage_table,
                title="📊 Usage Statistics (Today)",
                border_style="yellow",
                padding=(1, 1)
            )
            
            console.print(panel)
            
            # Show warning if usage is high
            if usage_percent > 80:
                console.print("⚠️  [red]Warning: You're approaching your monthly token limit![/red]")
            elif usage_percent > 50:
                console.print("💡 [yellow]Info: You've used over half of your monthly tokens.[/yellow]")
        else:
            console.print("❌ [red]Failed to load usage statistics[/red]")
    
    async def chat_session(self):
        """Start interactive chat session"""
        console.print("\n[bold cyan]💬 Chat Session Started[/bold cyan]")
        console.print("[dim]Type 'quit', 'exit', or 'bye' to end the session[/dim]")
        console.print("[dim]Type 'clear' to clear conversation history[/dim]")
        console.print()
        
        while True:
            try:
                user_input = Prompt.ask("[bold green]You[/bold green]")
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    console.print("👋 [yellow]Chat session ended[/yellow]")
                    break
                
                if user_input.lower() == 'clear':
                    self.conversation_history = []
                    console.print("🧹 [yellow]Conversation history cleared[/yellow]")
                    continue
                
                # Add user message to history
                self.conversation_history.append({"role": "user", "content": user_input})
                
                # Show typing indicator
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    task = progress.add_task("🤖 AI is thinking...", total=None)
                    
                    result = await self.client.chat_completion(self.conversation_history)
                
                if result["status_code"] == 200:
                    response_data = result["data"]
                    
                    if "choices" in response_data and response_data["choices"]:
                        ai_response = response_data["choices"][0]["message"]["content"]
                        
                        # Add AI response to history
                        self.conversation_history.append({"role": "assistant", "content": ai_response})
                        
                        # Display AI response
                        ai_panel = Panel(
                            ai_response,
                            title="🤖 KnockXPrime AI",
                            border_style="blue",
                            padding=(1, 2)
                        )
                        console.print(ai_panel)
                        
                        # Show usage info if available
                        if "usage_info" in response_data:
                            usage_info = response_data["usage_info"]
                            console.print(f"[dim]Tokens remaining today: {usage_info.get('tokens_remaining_today', 0):,}[/dim]")
                            console.print(f"[dim]Requests remaining today: {usage_info.get('requests_remaining_today', 0):,}[/dim]")
                    else:
                        console.print("❌ [red]No response from AI[/red]")
                
                elif result["status_code"] == 402:
                    # Payment required - token limit exceeded
                    error_data = result["data"]["detail"]
                    console.print(f"💳 [red]{error_data['message']}[/red]")
                    console.print("💡 [yellow]Consider upgrading your plan to continue chatting.[/yellow]")
                    break
                
                elif result["status_code"] == 429:
                    # Too many requests - request limit exceeded
                    error_data = result["data"]["detail"]
                    console.print(f"⏰ [red]{error_data['message']}[/red]")
                    console.print("💡 [yellow]You've reached your daily request limit. Try again tomorrow or upgrade your plan.[/yellow]")
                    break
                
                else:
                    error_msg = result["data"].get("detail", "Chat request failed")
                    console.print(f"❌ [red]{error_msg}[/red]")
                
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n👋 [yellow]Chat session interrupted[/yellow]")
                break
            except Exception as e:
                console.print(f"❌ [red]Error: {str(e)}[/red]")
    
    def logout(self):
        """Logout user"""
        self.client.clear_session()
        self.conversation_history = []
        console.print("👋 [yellow]Logged out successfully[/yellow]")
    
    async def run(self):
        """Main application loop"""
        # Load saved session
        self.client.load_session()
        
        # Display banner
        self.display_banner()
        
        # Check API connection
        if not await self.check_connection():
            console.print("🔧 [yellow]Please make sure the KnockXPrime AI server is running on http://localhost:8000[/yellow]")
            return
        
        console.print()
        
        while True:
            try:
                self.display_menu()
                console.print()
                
                if self.client.api_key:
                    # Authenticated menu
                    choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6"])
                    
                    if choice == "1":
                        await self.chat_session()
                    elif choice == "2":
                        await self.show_usage()
                    elif choice == "3":
                        await self.show_profile()
                    elif choice == "4":
                        await self.show_plans()
                    elif choice == "5":
                        self.logout()
                    elif choice == "6":
                        break
                else:
                    # Unauthenticated menu
                    choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
                    
                    if choice == "1":
                        await self.login_flow()
                    elif choice == "2":
                        await self.register_flow()
                    elif choice == "3":
                        await self.show_plans()
                    elif choice == "4":
                        console.print("🔧 [yellow]Settings coming soon![/yellow]")
                    elif choice == "5":
                        break
                
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n👋 [yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"❌ [red]Error: {str(e)}[/red]")
        
        console.print("🚀 [cyan]Thank you for using KnockXPrime AI![/cyan]")


@click.command()
@click.option('--server', default='http://localhost:8000', help='API server URL')
def main(server):
    """KnockXPrime AI CLI - Your Premium AI Assistant"""
    try:
        cli = KnockXPrimeCLI()
        cli.client.base_url = server
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Fatal error: {str(e)}[/red]")


if __name__ == "__main__":
    main()