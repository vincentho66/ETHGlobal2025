// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

//@dev The owner is the contract depolyer, and also the assets manager account.
contract Strategy is Ownable {

    address public user;

    //@dev Each user will deploy their own strategy contracts.
    constructor(address _user) {
        user = _user;
    }

    //@dev User needs to approve this contract to transfer their assets.
    function approve(address token) public {
        IERC20(token).approve(address(this), type(uint256).max);
    }

    //@dev After swapping, transfer tokens to user's EOA.
    function transfer(address token, uint256 amount) public onlyOwner {
        IERC20(token).transfer(user, amount);
    }

    //@dev Transfer tokens to swap to this contract.
    function transferFrom(address token, uint256 amount) public onlyOwner {
        IERC20(token).transferFrom(user, address(this), amount);
    }

    //@dev In case of tokens stuck in this contract.
    function rescue(address token, address to, uint256 amount) public onlyOwner {
        IERC20(token).transfer(to, amount);
    }
}