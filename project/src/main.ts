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
      walletAddress.innerText = `Wallet Address: ${address}`;
    } catch (err: any) {
      console.error("Connection failed:", err);
      walletAddress.innerText = "Wallet connection failed";
    }
  } else {
    walletAddress.innerText = "Please install MetaMask first";
  }
});
