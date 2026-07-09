pragma solidity >= 0.8.11 <= 0.8.11;

contract Ecommerce {
    string public client_data;
    string public block_transaction;
      
    //save client details	
    function addClientData(string memory cd) public {
       client_data = cd;	
    }
   //get client details
    function getClientData() public view returns (string memory) {
        return client_data;
    }

    function addBlockTransaction(string memory bt) public {
       block_transaction = bt;	
    }

    function getBlockTransaction() public view returns (string memory) {
        return block_transaction;
    }

    constructor() public {
        client_data = "";
	block_transaction="";
    }
}