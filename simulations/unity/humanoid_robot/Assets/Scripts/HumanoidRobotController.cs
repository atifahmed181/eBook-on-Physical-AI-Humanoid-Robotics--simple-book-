using UnityEngine;

public class HumanoidRobotController : MonoBehaviour
{
    public Animator animator;
    public float moveSpeed = 2.0f;
    public float turnSpeed = 100.0f;
    public Transform robotRoot;

    void Update()
    {
        HandleMovement();
        HandleAnimations();
    }

    void HandleMovement()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        Vector3 movement = new Vector3(horizontal, 0, vertical) * moveSpeed * Time.deltaTime;
        robotRoot.Translate(movement);
        
        if (horizontal != 0 || vertical != 0)
        {
            // Turn robot to face movement direction
            Vector3 targetDirection = new Vector3(horizontal, 0, vertical);
            Quaternion targetRotation = Quaternion.LookRotation(targetDirection);
            robotRoot.rotation = 
                Quaternion.RotateTowards(robotRoot.rotation, targetRotation, turnSpeed * Time.deltaTime);
        }
    }

    void HandleAnimations()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        // Blend walking/running animations based on movement
        if (vertical > 0.1f)
        {
            animator.SetFloat("Speed", vertical);
        }
        else
        {
            animator.SetFloat("Speed", 0);
        }
    }
}