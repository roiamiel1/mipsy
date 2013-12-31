lw $sp, 0($zero)
lw $a0, 4($zero)
lw $a1, 28($zero)
jal sort
j check_values

swap:
    lw $t0, 0($a0)
    lw $t1, 4($a0)
    slt $t2, $t1, $t0
    beq $t2, $zero, swap_else
    sw $t1, 0($a0)
    sw $t0, 4($a0)
    addi $v0, $zero, 1
    jr $ra
swap_else:
    addi $v0, $zero, 0
    jr $ra

sort:
    addi $sp,$sp, -20
    sw $ra, 16($sp)
    sw $s3, 12($sp)
    sw $s2, 8($sp)
    sw $s1, 4($sp)
    sw $s0, 0($sp)
    add $s0, $a0, $zero
    sll $a1, $a1, 2
    add $s1, $s0, $a1
    add $s2, $s0, $zero
    j for1_tst

for1_loop:
    addi $s3, $s2, -4
    j for2_tst
for2_loop:
    addi $s3, $s3, -4
for2_tst:
    slt $t0, $s3, $s0
    beq $t0, $zero, equal1
    j for2_exit
equal1:
    add $a0, $s3, $zero
    jal swap
    beq $v0, $zero, for2_exit
    j for2_loop
for2_exit:
    addi $s2, $s2, 4
for1_tst:
    slt $t0, $s2, $s1
    beq $t0, $zero, exit1
    j for1_loop

exit1:
    lw $s0, 0($sp)
    lw $s1, 4($sp)
    lw $s2, 8($sp)
    lw $s3, 12($sp)
    lw $ra, 16($sp)
    addi $sp, $sp, 20
    jr $ra
check_values:
    lw $t0, 0($zero)
    lw $t1, 4($zero)
    lw $t2, 8($zero)
    lw $t3, 12($zero)
    lw $t4, 16($zero)
    nop
