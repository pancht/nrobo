# nROBO - NextGen automation pytest backed testing framework

graph TD
    A[User Project] --> B[nrobo CLI / Runner]

    B --> C[Test Loader]
    B --> D[Test Executor]
    B --> E[Reporting Engine]

    C -->|Reads YAML/JSON| F[Test Suites]
    D -->|Runs with| G[PyTest]
    E --> H[Allure / HTML Reports]

    B --> I[Utilities]
    I --> J[Helpers / Validators]
    I --> K[Logging]

    B --> L[Build & Publish Script]
    L --> M[PyPI Packaging]
