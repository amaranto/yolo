import asyncio

async def func_a():
    print("Function A is running")
    await asyncio.sleep(3)
    print("Function A is done")
    return "Function A"

async def func_b():
    print("Function B is running")
    #await asyncio.sleep(3)
    print("Function B is done")
    return "Function B"

async def main():
    print("Main function is running")
    results = await asyncio.gather(func_a(), func_b())
    print("Main function is done")
    print(results)

asyncio.run(main())