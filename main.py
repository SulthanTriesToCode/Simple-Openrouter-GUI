import tkinter as tk
from tkinter import scrolledtext, messagebox
from openai import OpenAI # Updated import
import pyperclip
import os

# Global client variable, initialized later
client = None

def initialize_openai_client(api_key_value):
    """Initializes or re-initializes the OpenAI client."""
    global client
    if not api_key_value:
        # Don't print error here, handle in send_to_openai if needed at time of use
        client = None
        return False # Indicate failure

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key_value,
        )
        # Optional: Add a test call here to verify the key if needed
        print("OpenAI client initialized/updated successfully.")
        return True # Indicate success
    except Exception as e:
        print(f"Error initializing OpenAI client for OpenRouter: {e}")
        # Show error only if initialization fails with a key provided
        messagebox.showerror("API Initialization Error", f"Failed to initialize client: {e}\nPlease check your API Key.")
        client = None
        return False # Indicate failure

# --- Functions ---
def send_to_openai(): # Function name kept for simplicity, but uses 'client'
    # Ensure client is initialized with the current key from the entry field
    current_api_key = api_key_entry.get().strip()
    if not current_api_key:
        messagebox.showerror("API Error", "API Key is missing. Please enter your API Key.")
        return

    # Attempt to initialize/update the client with the current key
    if not initialize_openai_client(current_api_key):
         # Error message is shown within initialize_openai_client if it fails
         return

    # Check if client is valid after attempting initialization
    if not client:
        messagebox.showerror("API Error", "Client could not be initialized. Please check your API Key.")
        return

    prompt = input_text.get("1.0", tk.END).strip()
    if not prompt:
        messagebox.showwarning("Input Error", "Input text cannot be empty.")
        return

    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "Generating response...")
    output_text.config(state=tk.DISABLED)
    root.update_idletasks() # Update the UI to show the message

    try:
        # Get the model from the input field
        model_name = model_entry.get().strip()
        if not model_name:
            # If the field is empty when sending, show a warning or use a fallback.
            # For now, let's use a default, but ideally the user should provide one.
            messagebox.showwarning("Model Missing", "Model name is empty. Using default 'openai/gpt-3.5-turbo'.")
            model_name = "openai/gpt-3.5-turbo"

        # Using the chat completions endpoint with the initialized client
        response = client.chat.completions.create(
            model=model_name, # Use the specified or default model
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content.strip()

        output_text.config(state=tk.NORMAL)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, answer)
        output_text.config(state=tk.DISABLED)

    except Exception as e: # Catch generic Exception as specific errors might differ
         # Check for authentication-like errors if possible, otherwise show generic error
         if "authentication" in str(e).lower():
              messagebox.showerror("API Error", "Authentication failed. Please check your OpenRouter API key.")
         else:
              messagebox.showerror("API Error", f"An error occurred: {e}")
         output_text.config(state=tk.NORMAL)
         output_text.delete("1.0", tk.END)
         output_text.insert(tk.END, f"Error: {e}") # Show the actual error
         output_text.config(state=tk.DISABLED)
# Removed redundant specific exception block as the generic one handles it now.



def paste_from_clipboard():
    try:
        clipboard_content = pyperclip.paste()
        input_text.insert(tk.END, clipboard_content)
    except Exception as e:
        messagebox.showerror("Clipboard Error", f"Could not paste from clipboard: {e}")

def clear_input():
    input_text.delete("1.0", tk.END)

def copy_input():
    try:
        text_to_copy = input_text.get("1.0", tk.END).strip()
        if text_to_copy:
            pyperclip.copy(text_to_copy)
        else:
            messagebox.showwarning("Copy Warning", "Input text is empty.")
    except Exception as e:
        messagebox.showerror("Clipboard Error", f"Could not copy input text: {e}")

def copy_output():
    try:
        text_to_copy = output_text.get("1.0", tk.END).strip()
        if text_to_copy and text_to_copy != "Generating response..." and not text_to_copy.startswith("Error:"):
             pyperclip.copy(text_to_copy)
        elif not text_to_copy:
             messagebox.showwarning("Copy Warning", "Output text is empty.")
        else:
             messagebox.showwarning("Copy Warning", "Cannot copy status messages or errors.") # Prevent copying placeholder/error text
    except Exception as e:
        messagebox.showerror("Clipboard Error", f"Could not copy output text: {e}")


# --- Configuration File Handling ---
CONFIG_FILE = "config.txt"

def load_config():
    """Loads configuration from the file."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error loading config file: {e}")
    return config

def save_config():
    """Saves configuration to the file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            model_name = model_entry.get().strip()
            api_key_value = api_key_entry.get().strip()
            f.write(f"last_model={model_name}\n")
            f.write(f"api_key={api_key_value}\n") # Save API key
    except Exception as e:
        print(f"Error saving config file: {e}")

def on_closing():
    """Handles window closing event."""
    save_config()
    root.destroy()

# --- GUI Setup ---
root = tk.Tk()
root.title("Openrouter GUI") # Renamed window title
root.geometry("800x680") # Increased height further for API key input
root.protocol("WM_DELETE_WINDOW", on_closing) # Register save on close

# --- Load Config ---
config_data = load_config()
last_model = config_data.get("last_model", "")
saved_api_key = config_data.get("api_key", "")

# --- Initialize Client ---
# Initialize client once at startup with the saved key
initialize_openai_client(saved_api_key)


# --- GUI Setup ---

# Top frame for API Key and Model input
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=10, pady=(10, 5)) # Pack at the top

# API Key Input
api_key_frame = tk.Frame(top_frame)
api_key_frame.pack(fill=tk.X, pady=(0, 5)) # Add padding below API key row
api_key_label = tk.Label(api_key_frame, text="API Key:")
api_key_label.pack(side=tk.LEFT, padx=(0, 5))
api_key_entry = tk.Entry(api_key_frame, width=60, show="*") # Use show="*" to hide key
api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
api_key_entry.insert(0, saved_api_key) # Load saved API key

# Model Input
model_frame = tk.Frame(top_frame)
model_frame.pack(fill=tk.X)
model_label = tk.Label(model_frame, text="Model:  ") # Added space for alignment
model_label.pack(side=tk.LEFT, padx=(0, 5))
model_entry = tk.Entry(model_frame, width=60)
model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
model_entry.insert(0, last_model) # Set initial value from config or empty

# Main frame to hold text boxes side-by-side
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 0)) # Adjusted padding

# Input Text Box (Left)
input_frame = tk.Frame(main_frame)
input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5)) # Padding between boxes
input_label = tk.Label(input_frame, text="Input:")
input_label.pack(anchor='w')
input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10, width=40)
input_text.pack(fill=tk.BOTH, expand=True)

# Output Text Box (Right)
output_frame = tk.Frame(main_frame)
output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0)) # Padding between boxes
output_label = tk.Label(output_frame, text="Output:")
output_label.pack(anchor='w')
output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10, width=40, state=tk.DISABLED) # Start disabled
output_text.pack(fill=tk.BOTH, expand=True)

# Bottom Frame for Buttons
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.X, padx=10, pady=10)

# Configure columns for button placement
bottom_frame.columnconfigure(0, weight=1) # Left buttons area
bottom_frame.columnconfigure(1, weight=1) # Send button area
bottom_frame.columnconfigure(2, weight=1) # Right button area

# Left Buttons Frame
left_buttons_frame = tk.Frame(bottom_frame)
left_buttons_frame.grid(row=0, column=0, sticky='w')

paste_button = tk.Button(left_buttons_frame, text="Paste", command=paste_from_clipboard)
paste_button.pack(side=tk.LEFT, padx=2)

clear_button = tk.Button(left_buttons_frame, text="Clear Input", command=clear_input)
clear_button.pack(side=tk.LEFT, padx=2)

copy_input_button = tk.Button(left_buttons_frame, text="Copy Input", command=copy_input)
copy_input_button.pack(side=tk.LEFT, padx=2)

# Middle Send Button Frame
middle_button_frame = tk.Frame(bottom_frame)
middle_button_frame.grid(row=0, column=1) # Centered using grid layout

send_button = tk.Button(middle_button_frame, text="Send", command=send_to_openai, width=10)
send_button.pack()

# Right Buttons Frame
right_buttons_frame = tk.Frame(bottom_frame)
right_buttons_frame.grid(row=0, column=2, sticky='e')

copy_output_button = tk.Button(right_buttons_frame, text="Copy Output", command=copy_output)
copy_output_button.pack(side=tk.RIGHT, padx=2)


# --- Run ---
root.mainloop()