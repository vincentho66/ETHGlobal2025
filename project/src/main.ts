// src/main.ts
import { ethers } from "ethers";

// 強化 window 型別定義（TypeScript）
declare global {
  interface Window {
    ethereum?: any;
  }
}

const connectButton = document.getElementById("connectButton") as HTMLButtonElement;
const walletAddress = document.getElementById("walletAddress") as HTMLParagraphElement;

connectButton.addEventListener("click", async () => {
  if (typeof window.ethereum !== "undefined") {
    try {
      const provider = new ethers.providers.Web3Provider(window.ethereum);
      await provider.send("eth_requestAccounts", []);
      const signer = provider.getSigner();
      const address = await signer.getAddress();
      walletAddress.innerText = `錢包地址：${address}`;
    } catch (err) {
      console.error("連線失敗：", err);
      walletAddress.innerText = "❌ 錢包連接失敗";
    }
  } else {
    console.warn("MetaMask 未安裝");
    walletAddress.innerText = "⚠️ 請先安裝 MetaMask。";
  }
});
