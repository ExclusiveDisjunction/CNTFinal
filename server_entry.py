import Server.pool as pool

threadPool = pool.ThreadPool()

print("Setting up thread pool, binding on port 8081")
try:
    threadPool.bind(8080, "127.0.0.1")
    threadPool.listen()
    print("Entering main loop...\n")
    threadPool.mainLoop()

except KeyboardInterrupt:
    print(f"Keyboard interupt")
except OSError as e:
    print(f"OS Exception: {str(e)}")
except Exception as e:
    print(f"Unknown exception caught: {str(e)}")
finally:
    print(f"Shutting down thread pool")
    threadPool.kill()
    
print("Goodbye!")