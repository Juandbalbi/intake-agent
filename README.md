# Intake Agent

A dynamic conversational form assistant powered by PromptLayer that transforms traditional form-filling into natural conversations. This project enables organizations to create custom AI assistants that gather information through engaging dialogue rather than static forms.

## 🚀 Live Demo

Try out the application: [Intake Agent Demo](https://promptlayer-intake-agent.streamlit.app/)

*Note: You'll need your own OpenAI API key to test the application.*

## 🌟 Features

- **Dynamic Form Builder**: Create custom forms with various field types and validation rules
- **Conversational Interface**: Natural language interaction for data collection
- **Flexible Architecture**: Adaptable to different organizational needs

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Orchestration**: PromptLayer
- **Language Models**: OpenAI GPT
- **Data Storage**: Local JSON (agents.json)

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PromptLayer API Key
- OpenAI API Key

### Installation

1. Clone the repository:

```bash
git clone https://github.com/Juandbalbi/intake-agent.git
cd intake-agent
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:

```bash
PROMPTLAYER_API_KEY=your_promptlayer_key
```


### Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

## 💡 Usage

### Creating a Form Agent

1. Navigate to the "Create New Agent" tab
2. Name your agent and define its goal
3. Add form fields with:
   - Field name
   - Data type
   - Description
   - Optional example values
4. Click "Create Agent" to save

### Using the Form Agent

1. Switch to the "Talk to Agent" tab
2. Select your created agent
3. Start the conversation
4. The agent will naturally guide you through the form-filling process

## 🏗️ Project Structure

```
intake-agent/
├── src/
│ ├── core/ # Core configuration
│ ├── models/ # Data models
│ ├── pages/ # Streamlit pages
│ ├── streaming/ # Streaming functionality
│ └── utils/ # Utility functions
├── app.py # Application entry point
└── agents.json # Agent storage
```

## 🔄 Workflow

1. **Form Definition**: Organizations define their data collection needs
2. **Agent Creation**: System generates a specialized conversational agent
3. **Data Collection**: Agent naturally gathers information through conversation
4. **Validation**: Multi-step validation ensures data quality
5. **Storage**: Validated data is stored in structured format

## 🧪 Testing

The project includes a comprehensive evaluation system through PromptLayer:
- Behavioral test cases
- Data validation scenarios
- Conversation flow testing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- PromptLayer team for their platform and support
- Streamlit for the excellent UI framework
- OpenAI for their powerful language models

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.
