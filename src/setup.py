#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Copyright (c) 2025 Instructure, Inc. All rights reserved.
"""

from setuptools import setup, find_packages
import os

# execute this file to get VERSION in the local namespace, but don't import the module
exec(
    compile(
        open(
            os.path.join(os.path.dirname(__file__), "lib", "version.py"), "rb"
        ).read(),
        os.path.join(os.path.dirname(__file__), "version.py"),
        "exec",
    )
)

setup(
    name="otel-python-app",
    description="Python Application to demonstrate OpenTelemetry",
    version=".".join(map(str, VERSION)),
    packages=find_packages(),
    author="Francisco Gray",
    author_email="francisco.gray@instructure.com",
    install_requires=[
        "Flask>=3.0.2",
        "mysqlclient>=2.2.4",
        "PyMySQL>=1.1.0",
        "redis>=5.0.3",
        "opentelemetry-api>=1.25",
        "opentelemetry-sdk>=1.25",
        "opentelemetry-instrumentation-flask>=0.46b0",
        "opentelemetry-instrumentation-mysqlclient>=0.46b0",
        "opentelemetry-instrumentation-redis>=0.46b0",
        "opentelemetry-exporter-otlp-proto-grpc>=1.25",
        "opentelemetry-exporter-otlp-proto-http>=1.25"
    ],
)

