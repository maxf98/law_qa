import React from "react";
import styled, { keyframes } from "styled-components";

// Keyframes for the animation
const typingAnimation = keyframes`
  0%, 80%, 100% { 
    transform: scale(0);
  }
  40% { 
    transform: scale(1);
  }
`;

// Styled component for the dot
const Dot = styled.span`
  display: block;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color: var(--button-color); // Customize color
  margin: 0 3px;
  animation: ${typingAnimation} 1.4s infinite ease-in-out both;
`;

// Styled component for the container
const TypingIndicatorContainer = styled.div`
  display: inline-flex;
  align-items: center;
  justify-content: center;

  & > ${Dot}:nth-child(1) {
    animation-delay: -0.32s;
  }

  & > ${Dot}:nth-child(2) {
    animation-delay: -0.16s;
  }
`;

// React component
const TypingIndicator = () => {
  return (
    <TypingIndicatorContainer>
      <Dot></Dot>
      <Dot></Dot>
      <Dot></Dot>
    </TypingIndicatorContainer>
  );
};

export default TypingIndicator;
