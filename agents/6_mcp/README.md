# MCP (Multi-Agent Collaboration Platform) Projects

This directory contains labs and a complex multi-agent application simulating a market environment.

## Labs

The labs are a series of Jupyter notebooks that likely introduce the concepts used in the main application.

- **1_lab1.ipynb**: Introduction to the platform and basic agent interactions.
- **2_lab2.ipynb**: Focuses on specific components of the market simulation.
- **3_lab3.ipynb**: Explores agent strategies or market dynamics.
- **4_lab4.ipynb**: Covers advanced topics or a more complex simulation.
- **5_lab5.ipynb**: A final lab, possibly integrating all the concepts.

## Applications

### Simulated Market Environment

This is a sophisticated multi-agent system that simulates a financial market. It includes components for managing accounts, running a market, and defining trader agents.

- **app.py**: The main entry point for the application.
- **market.py** / **market_server.py**: The core of the market simulation, where assets are traded.
- **accounts.py** / **accounts_server.py**: Manages user or agent accounts and balances.
- **traders.py**: Defines the different types of trader agents and their strategies.
- **trading_floor.py**: The environment where the trader agents interact with the market.
- **database.py**: Handles data persistence for the application.
- **util.py**, **mcp_params.py**, **templates.py**, **tracers.py**: Various utility modules for configuration, templating, and tracing.
- **push_server.py**: Likely handles real-time updates to clients.
- **reset.py**: A script to reset the simulation to a default state.

## Community Contributions

This directory contains MCP-related projects contributed by the community.
