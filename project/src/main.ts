// main.ts
import { ethers } from "ethers";

const connectButton = document.getElementById("connectButton") as HTMLButtonElement;
const walletAddress = document.getElementById("walletAddress") as HTMLParagraphElement;

connectButton.addEventListener("click", async () => {
  if (window.ethereum) {
    try {
      const provider = new ethers.providers.Web3Provider(window.ethereum);
      await provider.send("eth_requestAccounts", []);
      const signer = provider.getSigner();
      const address = await signer.getAddress();
      walletAddress.innerText = `錢包地址：${address}`;
    } catch (err: any) {
      console.error("連線失敗：", err);
      walletAddress.innerText = "❌ 錢包連接失敗";
    }
  } else {
    walletAddress.innerText = "⚠️ 請先安裝 MetaMask。";
  }
});
