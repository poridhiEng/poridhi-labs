const sendDataBtn = document.getElementById('send-data-btn');
const resetBtn = document.getElementById('reset-btn');
const detailsPanel = document.getElementById('details-panel');
const sendPacket = document.getElementById('send-packet');
const receivePacket = document.getElementById('receive-packet');
const physicalConnection = document.getElementById('physical-connection');

const dataUnits = {
    application: "Data",
    presentation: "Data",
    session: "Data",
    transport: "Segment",
    network: "Packet",
    datalink: "Frame",
    physical: "Bits"
};

const layerDetails = {
    application: {
        send: 'Application data is prepared for network transmission',
        receive: 'Application receives and processes the data'
    },
    presentation: {
        send: 'Data is formatted, encrypted or compressed',
        receive: 'Data is decrypted and converted to application format'
    },
    session: {
        send: 'Session connection is established and managed',
        receive: 'Session integrity is verified'
    },
    transport: {
        send: 'Data is segmented and port numbers are added',
        receive: 'Segments are reassembled and ordered'
    },
    network: {
        send: 'IP addresses are added to create packets',
        receive: 'Packets are routed to correct destination'
    },
    datalink: {
        send: 'MAC addresses are added to create frames',
        receive: 'Frames are checked for transmission errors'
    },
    physical: {
        send: 'Binary data is transmitted across physical medium',
        receive: 'Binary data is received from physical medium'
    }
};

function updatePacketText(packet, layer, isReceiving = false) {
    const unitName = dataUnits[layer];
    packet.textContent = isReceiving ? 
        `Received ${unitName}` : 
        `Sending ${unitName}`;
}

function resetCommunication() {
    // Reset layers
    document.querySelectorAll('.layer').forEach(layer => {
        layer.classList.remove('active-send', 'active-receive');
    });

    // Reset packets
    sendPacket.style.opacity = '0';
    receivePacket.style.opacity = '0';
    sendPacket.style.top = '0';
    receivePacket.style.top = '0';
    
    // Reset text
    sendPacket.textContent = 'Data';
    receivePacket.textContent = 'Data';

    // Reset physical connection
    physicalConnection.classList.remove('active');
    
    // Reset details panel
    detailsPanel.innerHTML = `
        <h2 class="details-title">Inter-System Communication</h2>
        <p class="details-description">
            Click 'Send Data' to see how data travels through the OSI layers across two systems
        </p>
    `;
}

function activatePhysicalConnection() {
    return new Promise(resolve => {
        physicalConnection.classList.add('active');
        // Simulate transmission time across physical medium
        setTimeout(() => {
            resolve();
        }, 1500); // 1.5 seconds for physical transmission
    });
}

function deactivatePhysicalConnection() {
    physicalConnection.classList.remove('active');
}

async function startCommunication() {
    const layers = ['application', 'presentation', 'session', 'transport', 'network', 'datalink', 'physical'];
    
    // Reset before starting
    resetCommunication();
    
    // Show sending packet
    sendPacket.style.opacity = '1';
    sendPacket.style.top = '0';

    // Process sending through layers
    for (let i = 0; i < layers.length; i++) {
        const layer = layers[i];
        const senderLayer = document.querySelector(`[data-layer="${layer}"][data-system="sender"]`);
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        senderLayer.classList.add('active-send');
        updatePacketText(sendPacket, layer);
        sendPacket.style.top = `${senderLayer.offsetTop}px`;

        // Update details panel
        detailsPanel.innerHTML = `
            <h2 class="details-title">Sending at ${layer.charAt(0).toUpperCase() + layer.slice(1)} Layer</h2>
            <p class="details-description">
                Current Data Unit: ${dataUnits[layer]}<br>
                ${layerDetails[layer].send}
            </p>
        `;

        // When reaching physical layer, activate physical connection
        if (layer === 'physical') {
            await activatePhysicalConnection();
            
            // Begin receiving process
            receivePacket.style.opacity = '1';
            const physicalReceiverLayer = document.querySelector('[data-layer="physical"][data-system="receiver"]');
            receivePacket.style.top = `${physicalReceiverLayer.offsetTop}px`;

            // Process receiving through layers in reverse
            const reversedLayers = [...layers].reverse();
            for (let j = 0; j < reversedLayers.length; j++) {
                const revLayer = reversedLayers[j];
                const receiverLayer = document.querySelector(`[data-layer="${revLayer}"][data-system="receiver"]`);
                
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                receiverLayer.classList.add('active-receive');
                updatePacketText(receivePacket, revLayer, true);
                receivePacket.style.top = `${receiverLayer.offsetTop}px`;

                // Update details panel for receiving
                detailsPanel.innerHTML = `
                    <h2 class="details-title">Receiving at ${revLayer.charAt(0).toUpperCase() + revLayer.slice(1)} Layer</h2>
                    <p class="details-description">
                        Current Data Unit: ${dataUnits[revLayer]}<br>
                        ${layerDetails[revLayer].receive}
                    </p>
                `;

                // Deactivate physical connection after data has moved past physical layer
                if (revLayer === 'datalink') {
                    deactivatePhysicalConnection();
                }
            }

            // Reset after complete cycle
            setTimeout(resetCommunication, 2000);
        }
    }
}

// Event Listeners
sendDataBtn.addEventListener('click', startCommunication);
resetBtn.addEventListener('click', resetCommunication);