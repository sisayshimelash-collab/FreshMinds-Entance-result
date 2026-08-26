import asyncio
from eaes_client import EAESClient

async def test():
    client = EAESClient()
    await client.start()
    res = await client.check_result("00177069", "Endale")
    print("Status:", res.status)
    if res.student:
        print("Student Full Name:", res.student.full_name)
        print("Admission No:", res.student.admission_no)
    print("Results:")
    for r in res.results:
        print(f"  {r.subject}: {r.result}")
    await client.close()

if __name__ == "__main__":
    asyncio.run(test())
