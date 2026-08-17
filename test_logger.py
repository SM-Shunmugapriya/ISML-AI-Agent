import time

from agents.workflow import app


print("\n========== FIRST RUN ==========")

start_time = time.perf_counter()

result1 = app.invoke({
    "user_query": "I want to learn Python programming"
})

time1 = time.perf_counter() - start_time

print(f"First Run Time: {time1:.2f} seconds")


print("\n========== SECOND RUN ==========")

start_time = time.perf_counter()

result2 = app.invoke({
    "user_query": "I want to learn Python programming"
})

time2 = time.perf_counter() - start_time

print(f"Second Run Time: {time2:.2f} seconds")