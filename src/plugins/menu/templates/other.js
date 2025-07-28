document.addEventListener('DOMContentLoaded', function() {
            const body = document.querySelector('body');
            const bubbleCount = 15;
            
            for (let i = 0; i < bubbleCount; i++) {
                const bubble = document.createElement('div');
                bubble.classList.add('bubble');

                const size = Math.random() * 100 + 20;
                const posX = Math.random() * 100;
                const posY = Math.random() * 100;
                
                bubble.style.width = `${size}px`;
                bubble.style.height = `${size}px`;
                bubble.style.left = `${posX}%`;
                bubble.style.top = `${posY}%`;
                
                const colors = [
                    'rgba(255, 158, 216, 0.3)',
                    'rgba(164, 220, 255, 0.3)',
                    'rgba(255, 215, 110, 0.3)',
                    'rgba(160, 231, 160, 0.3)'
                ];
                bubble.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                
                bubble.style.animationDelay = `${Math.random() * 5}s`;
                
                body.appendChild(bubble);
            }
        });