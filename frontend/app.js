const API_URL = 'https://blockchain-2-nnio.onrender.com';

// Load blockchain data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadBlockchain();
    
    // Set up form submission
    document.getElementById('transaction-form').addEventListener('submit', handleTransactionSubmit);
    
    // Set up track button
    document.getElementById('track-btn').addEventListener('click', handleTrackProduct);
    
    // Set up refresh button
    document.getElementById('refresh-btn').addEventListener('click', () => {
        loadStats();
        loadBlockchain();
    });
    
    // Set up mine button
    document.getElementById('mine-btn').addEventListener('click', handleMine);
});

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();
        
        document.getElementById('total-blocks').textContent = data.total_blocks;
        document.getElementById('total-transactions').textContent = data.total_transactions;
        document.getElementById('total-products').textContent = data.total_products;
        document.getElementById('pending-transactions').textContent = data.pending_transactions;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadBlockchain() {
    try {
        const response = await fetch(`${API_URL}/chain`);
        const data = await response.json();
        
        displayBlockchain(data.chain);
    } catch (error) {
        console.error('Error loading blockchain:', error);
        document.getElementById('blockchain').innerHTML = 
            '<div class="error">Error loading blockchain. Make sure the backend server is running.</div>';
    }
}

function displayBlockchain(chain) {
    const blockchainDiv = document.getElementById('blockchain');
    
    if (chain.length === 0) {
        blockchainDiv.innerHTML = '<div class="empty-state">No blocks in the chain yet.</div>';
        return;
    }
    
    blockchainDiv.innerHTML = chain.map(block => {
        const transactionsHtml = block.transactions.map(tx => `
            <div class="transaction">
                <div class="transaction-header">
                    ${tx.product_name} (${tx.product_id})
                </div>
                <div class="transaction-details">
                    <div><strong>From:</strong> ${tx.sender}</div>
                    <div><strong>To:</strong> ${tx.recipient}</div>
                    <div><strong>Location:</strong> ${tx.location}</div>
                    <div><strong>Status:</strong> <span class="status-badge status-${tx.status.replace('-', '-')}">${tx.status}</span></div>
                </div>
            </div>
        `).join('');
        
        const date = new Date(block.timestamp * 1000).toLocaleString();
        
        return `
            <div class="block">
                <div class="block-header">
                    <span>Block #${block.index}</span>
                    <span>${date}</span>
                </div>
                <div class="block-info">
                    <div><strong>Proof:</strong> ${block.proof}</div>
                    <div><strong>Previous Hash:</strong> ${block.previous_hash.substring(0, 20)}...</div>
                    <div><strong>Transactions:</strong> ${block.transactions.length}</div>
                </div>
                ${transactionsHtml}
            </div>
        `;
    }).join('');
}

async function handleTransactionSubmit(e) {
    e.preventDefault();
    
    const formData = {
        sender: document.getElementById('sender').value,
        recipient: document.getElementById('recipient').value,
        product_id: document.getElementById('product-id').value,
        product_name: document.getElementById('product-name').value,
        location: document.getElementById('location').value,
        status: document.getElementById('status').value
    };
    
    try {
        const response = await fetch(`${API_URL}/transactions/new`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Transaction added successfully! It will be included in the next block.', 'success');
            document.getElementById('transaction-form').reset();
            loadStats();
        } else {
            showMessage('Error: ' + (data.message || 'Failed to add transaction'), 'error');
        }
    } catch (error) {
        console.error('Error submitting transaction:', error);
        showMessage('Error connecting to server. Make sure the backend is running.', 'error');
    }
}

async function handleTrackProduct() {
    const productId = document.getElementById('track-product-id').value.trim();
    
    if (!productId) {
        showMessage('Please enter a product ID', 'error');
        return;
    }
    
    const historyDiv = document.getElementById('product-history');
    historyDiv.innerHTML = '<div class="loading">Loading product history...</div>';
    
    try {
        const response = await fetch(`${API_URL}/products/${productId}/history`);
        const data = await response.json();
        
        if (data.history.length === 0) {
            historyDiv.innerHTML = '<div class="empty-state">No history found for this product ID.</div>';
            return;
        }
        
        historyDiv.innerHTML = data.history.map(item => {
            const date = new Date(item.timestamp * 1000).toLocaleString();
            const tx = item.transaction;
            
            return `
                <div class="history-item">
                    <div class="history-item-header">
                        Block #${item.block_index} - ${date}
                    </div>
                    <div class="history-item-details">
                        <div><strong>Product:</strong> ${tx.product_name}</div>
                        <div><strong>From:</strong> ${tx.sender} → <strong>To:</strong> ${tx.recipient}</div>
                        <div><strong>Location:</strong> ${tx.location}</div>
                        <div><strong>Status:</strong> <span class="status-badge status-${tx.status.replace('-', '-')}">${tx.status}</span></div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error tracking product:', error);
        historyDiv.innerHTML = '<div class="error">Error loading product history. Make sure the backend server is running.</div>';
    }
}

async function handleMine() {
    const mineBtn = document.getElementById('mine-btn');
    mineBtn.disabled = true;
    mineBtn.textContent = 'Mining...';
    
    try {
        const response = await fetch(`${API_URL}/mine`, {
            method: 'GET'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Block mined successfully!', 'success');
            loadStats();
            loadBlockchain();
        } else {
            showMessage('Error mining block', 'error');
        }
    } catch (error) {
        console.error('Error mining:', error);
        showMessage('Error connecting to server.', 'error');
    } finally {
        mineBtn.disabled = false;
        mineBtn.textContent = 'Mine Block';
    }
}

function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = type;
    messageDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}


