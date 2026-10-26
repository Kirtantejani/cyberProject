// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Minimal auditable registry and owner-controlled access-request workflow.
/// Never store plaintext files, encryption keys, or private information on-chain.
contract SecureFileSharing {
    enum RequestStatus { None, Pending, Approved, Rejected }

    struct FileRecord {
        address owner;
        bytes32 contentHash;
        bool exists;
    }
    struct AccessRequest {
        address requester;
        RequestStatus status;
        uint256 requestedAt;
        uint256 decidedAt;
    }

    mapping(bytes32 => FileRecord) public files;
    mapping(bytes32 => mapping(address => AccessRequest)) public requests;

    event FileRegistered(bytes32 indexed fileId, address indexed owner, bytes32 contentHash);
    event AccessRequested(bytes32 indexed fileId, address indexed requester, uint256 timestamp);
    event AccessDecided(bytes32 indexed fileId, address indexed requester, bool approved, address indexed owner);

    modifier onlyFileOwner(bytes32 fileId) {
        require(files[fileId].exists, "Unknown file");
        require(files[fileId].owner == msg.sender, "Only owner");
        _;
    }

    function registerFile(bytes32 fileId, bytes32 contentHash) external {
        require(!files[fileId].exists, "File already registered");
        files[fileId] = FileRecord(msg.sender, contentHash, true);
        emit FileRegistered(fileId, msg.sender, contentHash);
    }

    function requestAccess(bytes32 fileId) external {
        require(files[fileId].exists, "Unknown file");
        require(msg.sender != files[fileId].owner, "Owner already has access");
        AccessRequest storage req = requests[fileId][msg.sender];
        require(req.status != RequestStatus.Pending, "Request pending");
        req.requester = msg.sender;
        req.status = RequestStatus.Pending;
        req.requestedAt = block.timestamp;
        req.decidedAt = 0;
        emit AccessRequested(fileId, msg.sender, block.timestamp);
    }

    function decideAccess(bytes32 fileId, address requester, bool approve) external onlyFileOwner(fileId) {
        AccessRequest storage req = requests[fileId][requester];
        require(req.status == RequestStatus.Pending, "No pending request");
        req.status = approve ? RequestStatus.Approved : RequestStatus.Rejected;
        req.decidedAt = block.timestamp;
        emit AccessDecided(fileId, requester, approve, msg.sender);
    }

    function isApproved(bytes32 fileId, address requester) external view returns (bool) {
        return requests[fileId][requester].status == RequestStatus.Approved;
    }
}
