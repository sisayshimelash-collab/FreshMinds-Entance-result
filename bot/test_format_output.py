import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from eaes_client import EAESClient
import messages as msg

async def test_students():
    client = EAESClient()
    await client.start()
    
    test_cases = [
        ("00445959", "Tsedal"),
        ("00629726", "Aschalew"),
        ("00177069", "Endale"),
    ]
    
    for adm, name in test_cases:
        res = await client.check_result(adm, name)
        print(f"\n=== Test: {adm} {name} ===")
        print("Status:", res.status)
        if res.student:
            text = msg.format_result_success(res.student, res.results)
            print("Formatted Telegram Message:")
            print(text.encode("utf-8", errors="replace").decode("utf-8"))
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_students())
