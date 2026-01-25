#!/usr/bin/env python3
"""
Resilience Patterns Generator

Генерация resilience patterns: circuit breaker, retry, timeout, bulkhead, rate limiting.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import threading


class CircuitState(Enum):
    """Circuit Breaker States"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RetryStrategy(Enum):
    """Retry Strategy Types"""
    FIXED = "fixed"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"


@dataclass
class CircuitBreakerConfig:
    """Circuit Breaker Configuration"""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 60.0
    half_open_max_requests: int = 3


@dataclass
class RetryConfig:
    """Retry Configuration"""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    retry_on_exceptions: List[type] = field(default_factory=lambda: [Exception])


@dataclass
class BulkheadConfig:
    """Bulkhead Pattern Configuration"""
    max_concurrent_calls: int = 10
    max_wait_duration: float = 1.0


@dataclass
class RateLimitConfig:
    """Rate Limiting Configuration"""
    max_requests: int = 100
    window_seconds: float = 60.0


class CircuitBreaker:
    """Circuit Breaker Pattern Implementation"""

    def __init__(self, config: CircuitBreakerConfig):
        """
        Инициализация circuit breaker

        Args:
            config: Circuit breaker configuration
        """
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self._lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.success_count = 0

    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time is None:
            return False

        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.timeout_seconds

    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state

    def reset(self):
        """Manually reset circuit breaker"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None


class RetryPattern:
    """Retry Pattern Implementation"""

    def __init__(self, config: RetryConfig):
        """
        Инициализация retry pattern

        Args:
            config: Retry configuration
        """
        self.config = config

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        delay = self.config.initial_delay

        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                # Check if should retry on this exception
                if not any(isinstance(e, exc_type) for exc_type in self.config.retry_on_exceptions):
                    raise

                # Don't sleep after last attempt
                if attempt < self.config.max_attempts - 1:
                    time.sleep(delay)

                    # Calculate next delay
                    if self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                        delay = min(delay * self.config.backoff_multiplier, self.config.max_delay)
                    elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
                        delay = min(delay + self.config.initial_delay, self.config.max_delay)
                    # FIXED strategy keeps same delay

        # All retries failed
        raise last_exception


class BulkheadPattern:
    """Bulkhead Pattern Implementation"""

    def __init__(self, config: BulkheadConfig):
        """
        Инициализация bulkhead pattern

        Args:
            config: Bulkhead configuration
        """
        self.config = config
        self.semaphore = threading.Semaphore(config.max_concurrent_calls)

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with bulkhead protection

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If max concurrent calls exceeded or function fails
        """
        acquired = self.semaphore.acquire(timeout=self.config.max_wait_duration)

        if not acquired:
            raise Exception("Bulkhead limit reached - too many concurrent requests")

        try:
            return func(*args, **kwargs)
        finally:
            self.semaphore.release()


class RateLimiter:
    """Rate Limiting Pattern Implementation"""

    def __init__(self, config: RateLimitConfig):
        """
        Инициализация rate limiter

        Args:
            config: Rate limiting configuration
        """
        self.config = config
        self.requests: List[datetime] = []
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        """
        Check if request is allowed

        Returns:
            True if request is allowed, False otherwise
        """
        with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=self.config.window_seconds)

            # Remove old requests outside window
            self.requests = [req_time for req_time in self.requests if req_time > window_start]

            # Check if under limit
            if len(self.requests) < self.config.max_requests:
                self.requests.append(now)
                return True

            return False

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with rate limiting

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If rate limit exceeded or function fails
        """
        if not self.allow_request():
            raise Exception("Rate limit exceeded")

        return func(*args, **kwargs)


class ResiliencePatternGenerator:
    """Resilience Patterns Code Generator"""

    def __init__(self):
        """Инициализация resilience pattern generator"""
        pass

    def generate_circuit_breaker_code(self,
                                     language: str = "python",
                                     config: Optional[CircuitBreakerConfig] = None) -> str:
        """
        Generate circuit breaker code

        Args:
            language: Target language (python, go, java)
            config: Circuit breaker configuration

        Returns:
            Generated code
        """
        if config is None:
            config = CircuitBreakerConfig()

        if language == "python":
            return self._generate_python_circuit_breaker(config)
        elif language == "go":
            return self._generate_go_circuit_breaker(config)
        elif language == "java":
            return self._generate_java_circuit_breaker(config)
        else:
            return self._generate_python_circuit_breaker(config)

    def generate_retry_code(self,
                           language: str = "python",
                           config: Optional[RetryConfig] = None) -> str:
        """
        Generate retry pattern code

        Args:
            language: Target language
            config: Retry configuration

        Returns:
            Generated code
        """
        if config is None:
            config = RetryConfig()

        if language == "python":
            return self._generate_python_retry(config)
        elif language == "go":
            return self._generate_go_retry(config)
        else:
            return self._generate_python_retry(config)

    def generate_combined_pattern(self,
                                  service_name: str,
                                  language: str = "python") -> str:
        """
        Generate code with combined resilience patterns

        Args:
            service_name: Service name
            language: Target language

        Returns:
            Generated code with all patterns
        """
        if language == "python":
            return self._generate_python_combined(service_name)
        elif language == "go":
            return self._generate_go_combined(service_name)
        else:
            return self._generate_python_combined(service_name)

    def _generate_python_circuit_breaker(self, config: CircuitBreakerConfig) -> str:
        """Generate Python circuit breaker code"""
        return f'''from enum import Enum
from datetime import datetime
import threading

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self):
        self.failure_threshold = {config.failure_threshold}
        self.success_threshold = {config.success_threshold}
        self.timeout = {config.timeout_seconds}
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self._lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitState.CLOSED

    def _on_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

    def _should_attempt_reset(self):
        if not self.last_failure_time:
            return False
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout
'''

    def _generate_python_retry(self, config: RetryConfig) -> str:
        """Generate Python retry code"""
        return f'''import time

class RetryPattern:
    def __init__(self):
        self.max_attempts = {config.max_attempts}
        self.initial_delay = {config.initial_delay}
        self.max_delay = {config.max_delay}
        self.backoff_multiplier = {config.backoff_multiplier}

    def execute(self, func, *args, **kwargs):
        delay = self.initial_delay

        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_attempts - 1:
                    time.sleep(delay)
                    delay = min(delay * self.backoff_multiplier, self.max_delay)
                else:
                    raise
'''

    def _generate_python_combined(self, service_name: str) -> str:
        """Generate Python code with combined patterns"""
        return f'''from resilience_patterns import CircuitBreaker, RetryPattern, RateLimiter
import httpx

class {service_name}Client:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.circuit_breaker = CircuitBreaker()
        self.retry = RetryPattern()
        self.rate_limiter = RateLimiter()

    async def call_api(self, endpoint: str):
        """Call API with resilience patterns"""

        def make_request():
            # Rate limiting
            return self.rate_limiter.execute(
                # Circuit breaker
                lambda: self.circuit_breaker.call(
                    # Retry
                    lambda: self.retry.execute(
                        self._http_request, endpoint
                    )
                )
            )

        return await make_request()

    async def _http_request(self, endpoint: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{{self.base_url}}{{endpoint}}")
            response.raise_for_status()
            return response.json()
'''

    def _generate_go_circuit_breaker(self, config: CircuitBreakerConfig) -> str:
        """Generate Go circuit breaker code"""
        return f'''package main

import (
    "errors"
    "sync"
    "time"
)

type CircuitState int

const (
    Closed CircuitState = iota
    Open
    HalfOpen
)

type CircuitBreaker struct {{
    failureThreshold int
    successThreshold int
    timeout          time.Duration
    state            CircuitState
    failureCount     int
    successCount     int
    lastFailureTime  time.Time
    mutex            sync.Mutex
}}

func NewCircuitBreaker() *CircuitBreaker {{
    return &CircuitBreaker{{
        failureThreshold: {config.failure_threshold},
        successThreshold: {config.success_threshold},
        timeout:          {config.timeout_seconds} * time.Second,
        state:            Closed,
    }}
}}

func (cb *CircuitBreaker) Call(fn func() error) error {{
    cb.mutex.Lock()
    if cb.state == Open {{
        if cb.shouldAttemptReset() {{
            cb.state = HalfOpen
            cb.successCount = 0
        }} else {{
            cb.mutex.Unlock()
            return errors.New("circuit breaker is OPEN")
        }}
    }}
    cb.mutex.Unlock()

    err := fn()
    if err != nil {{
        cb.onFailure()
        return err
    }}

    cb.onSuccess()
    return nil
}}
'''

    def _generate_go_retry(self, config: RetryConfig) -> str:
        """Generate Go retry code"""
        return f'''package main

import (
    "time"
)

type RetryConfig struct {{
    MaxAttempts       int
    InitialDelay      time.Duration
    MaxDelay          time.Duration
    BackoffMultiplier float64
}}

func Retry(fn func() error, config RetryConfig) error {{
    delay := config.InitialDelay

    for attempt := 0; attempt < config.MaxAttempts; attempt++ {{
        err := fn()
        if err == nil {{
            return nil
        }}

        if attempt < config.MaxAttempts-1 {{
            time.Sleep(delay)
            delay = time.Duration(float64(delay) * config.BackoffMultiplier)
            if delay > config.MaxDelay {{
                delay = config.MaxDelay
            }}
        }} else {{
            return err
        }}
    }}

    return nil
}}
'''

    def _generate_go_combined(self, service_name: str) -> str:
        """Generate Go code with combined patterns"""
        return f'''package main

import (
    "context"
    "net/http"
)

type {service_name}Client struct {{
    baseURL        string
    circuitBreaker *CircuitBreaker
    client         *http.Client
}}

func New{service_name}Client(baseURL string) *{service_name}Client {{
    return &{service_name}Client{{
        baseURL:        baseURL,
        circuitBreaker: NewCircuitBreaker(),
        client:         &http.Client{{}},
    }}
}}

func (c *{service_name}Client) CallAPI(ctx context.Context, endpoint string) error {{
    return c.circuitBreaker.Call(func() error {{
        return Retry(func() error {{
            return c.httpRequest(ctx, endpoint)
        }}, RetryConfig{{
            MaxAttempts:       3,
            InitialDelay:      time.Second,
            MaxDelay:          time.Minute,
            BackoffMultiplier: 2.0,
        }})
    }})
}}
'''

    def _generate_java_circuit_breaker(self, config: CircuitBreakerConfig) -> str:
        """Generate Java circuit breaker code (Resilience4j style)"""
        return f'''import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;

import java.time.Duration;

public class ServiceClient {{
    private final CircuitBreaker circuitBreaker;

    public ServiceClient() {{
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold({config.failure_threshold})
            .waitDurationInOpenState(Duration.ofSeconds({config.timeout_seconds}))
            .build();

        CircuitBreakerRegistry registry = CircuitBreakerRegistry.of(config);
        this.circuitBreaker = registry.circuitBreaker("serviceClient");
    }}

    public String callService() {{
        return circuitBreaker.executeSupplier(() -> {{
            // Your service call here
            return "result";
        }});
    }}
}}
'''
