#!/usr/bin/env python3
"""Basic usage examples of the WAND programmatic API."""

from dir_wand import create_directories, run_commands


def example_1_simple_creation():
    """Create simple sequential directories."""
    print("Example 1: Simple directory creation")
    print("=" * 50)

    stats = create_directories(
        template="experiment_{num}",
        output_dir="/tmp/wand_examples/simple",
        num=range(5)
    )

    print(f"\nCreated {stats['directories']} directories")
    print(f"Created {stats['files']} files")
    print()


def example_2_multiple_placeholders():
    """Create directories with multiple placeholders."""
    print("Example 2: Multiple placeholders")
    print("=" * 50)

    stats = create_directories(
        template="sim_{scenario}_{seed}",
        output_dir="/tmp/wand_examples/multi",
        scenario=["baseline", "treatment", "control"],
        seed=[100, 200, 300]
    )

    print(f"\nCreated {stats['directories']} directories")
    print()


def example_3_with_commands():
    """Create directories and run commands."""
    print("Example 3: Create and run commands")
    print("=" * 50)

    stats = create_directories(
        template="job_{id}",
        output_dir="/tmp/wand_examples/jobs",
        id=range(1, 6),
        run_command="cd job_{id} && echo 'Processing job {id}' > output.txt"
    )

    print(f"\nCreated {stats['directories']} directories")
    print(f"Executed {stats['commands']} commands")
    print()


def example_4_run_commands_only():
    """Run commands in existing directories."""
    print("Example 4: Run commands only (no template)")
    print("=" * 50)

    # First, ensure directories exist
    create_directories(
        template="exp_{num}",
        output_dir="/tmp/wand_examples/existing",
        num=range(3),
        silent=True
    )

    # Now run commands in them
    stats = run_commands(
        "cd /tmp/wand_examples/existing/exp_{num} && echo 'Analyzed {num}' > results.txt",
        num=range(3)
    )

    print(f"\nExecuted {stats['commands']} commands")
    print()


def example_5_silent_mode():
    """Create directories silently."""
    print("Example 5: Silent mode")
    print("=" * 50)

    stats = create_directories(
        template="test_{num}",
        output_dir="/tmp/wand_examples/silent",
        num=range(10),
        silent=True  # No output during creation
    )

    # But we can still see the stats
    print(f"Silently created {stats['directories']} directories")
    print(f"Made {stats['swaps']} placeholder replacements")
    print()


def example_6_using_lists():
    """Use explicit lists for placeholder values."""
    print("Example 6: Using explicit value lists")
    print("=" * 50)

    stats = create_directories(
        template="model_{name}",
        output_dir="/tmp/wand_examples/models",
        name=["resnet50", "vgg16", "inception", "transformer"]
    )

    print(f"\nCreated {stats['directories']} directories")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("WAND Programmatic API Examples")
    print("=" * 50 + "\n")

    example_1_simple_creation()
    example_2_multiple_placeholders()
    example_3_with_commands()
    example_4_run_commands_only()
    example_5_silent_mode()
    example_6_using_lists()

    print("=" * 50)
    print("All examples complete!")
    print("Check /tmp/wand_examples/ for created directories")
    print("=" * 50)
