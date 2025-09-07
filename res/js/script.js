// --- Code for Modal on the Landing Page ---

// Get all necessary elements from the DOM
const modal = document.getElementById('popupModal');
const closeModalBtn = document.getElementById('closeModal');
const joinChatroomBodyBtn = document.getElementById('joinChatroomBody');

// This check ensures the following code only runs if the modal elements exist on the current page.
if (modal && closeModalBtn && joinChatroomBodyBtn) {
    // Function to open the modal
    const openModal = () => {
        modal.classList.remove('hidden');
    };

    // Function to close the modal
    const closeModal = () => {
        modal.classList.add('hidden');
    };

    // Add event listeners to the "Join Chatroom" button
    joinChatroomBodyBtn.addEventListener('click', openModal);
    closeModalBtn.addEventListener('click', closeModal);

    // Allow closing the modal by clicking on the background overlay
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Prevent closing modal when clicking inside the content area
    modal.querySelector('div').addEventListener('click', (event) => {
        event.stopPropagation();
    });
}

// --- You can add JavaScript for the chatroom page below this line in the future ---