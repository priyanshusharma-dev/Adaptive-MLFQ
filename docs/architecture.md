# Architecture Documentation

## Overview
Adaptive MLFQ is a web-based scheduling simulator that executes discrete-event simulations to compare standard Multilevel Feedback Queue scheduling with an AI-driven adaptive approach.

## Components

The system follows a clean, decoupled architecture consisting of two primary layers: a FastAPI Python Backend and a React/Vite TypeScript Frontend.

### 1. Frontend (React + Vite)
- **Framework**: React via Vite, implemented in TypeScript.
- **Styling**: Tailwind CSS for UI components.
- **Visualization**: Recharts for metrics and custom SVG/Canvas rendering for Gantt charts and Queue movement.
- **Responsibility**: Provides the UI for simulation configuration, process construction, workload generation, visualization of queue transitions, Gantt charts, and comparison analytics. No scheduling logic resides here.

### 2. Backend API (FastAPI)
- **Framework**: FastAPI for handling REST API requests and responses.
- **Validation**: Pydantic for strict schema validation of inputs and outputs.
- **Responsibility**: Exposes the underlying scheduling engine, simulation services, and machine learning models to the web.

### 3. Simulation Engine
- **Paradigm**: Discrete-event simulation.
- **Responsibility**: Maintains a simulated clock and processes events (arrivals, CPU bursts, I/O blocking, completions) deterministically without relying on actual OS threads. Operates completely independent of the web API layer.

### 4. Scheduling Logic
- **Standard MLFQ (Phase 1)**: Traditional rule-based scheduling with multiple configurable queues, priority levels, time quanta, demotion on quantum expiry, promotion on I/O return, and starvation-prevention mechanisms (priority boosting).
- **Adaptive MLFQ (Phase 2)**: Extends standard MLFQ by overriding scheduling decisions based on machine learning classifications (CPU Bound, I/O Bound, Interactive). It dynamically adjusts time quanta and queue assignments.

### 5. AI / Behaviour Predictor
- **Technology**: scikit-learn (RandomForestClassifier).
- **Responsibility**: Extracts feature vectors from process execution histories (e.g., average CPU burst, I/O frequency, burst variance) and classifies the process type.

### 6. Metrics & Analysis Engine
- **Responsibility**: Calculates Average Waiting Time, Response Time, Turnaround Time, Throughput, Context Switches, Starvation Status, and Jain's Fairness Index for individual processes and the entire workload.

### 7. Database
- **Technology**: SQLite.
- **Responsibility**: Stores experiment configurations, workloads, simulated events, adaptive decisions, and metric results for long-term tracking and reproducibility.

## System Flow
1. User configures a workload via the Frontend.
2. The config is POSTed to the Backend API.
3. The API passes data to the Simulation Service.
4. The Simulation Engine initializes standard or adaptive schedulers.
5. Events are processed chronologically. If Adaptive MLFQ is used, the AI Predictor classifies processes dynamically and adjusts the scheduler state.
6. Execution segments (Gantt) and calculated metrics are extracted.
7. Results are saved to SQLite and returned to the Frontend.
8. Frontend renders the results interactively.
